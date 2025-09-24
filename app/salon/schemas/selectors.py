import graphene
import jsonpickle
from datetime import datetime
from graphene.types.json import JSONString
from salon.models import *
from core.utils.tf_utils import (
    get_amount_with_currency_code,
    get_user_file_URL,
    convert_string_to_float,
    get_customer_file_URL,
)
from salon.models.setting import get_tax_settings
from graphql_jwt.decorators import login_required


class SelectorDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.Field(JSONString)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_dataset = graphene.Field(
        SelectorDataModelType,
        inKey=graphene.String(required=True),
        booking_id=graphene.Int(required=False),
    )

    @login_required
    def resolve_salon_dataset(self, info, inKey, **kwargs):
        DS = {}
        totalCount = 0
        org = info.context.user.get_organization()
        if inKey == "booking_item":
            booking_id = kwargs.get("booking_id", None)
            if not booking_id:
                raise Exception("Booking Id is required.")
            booking = Booking.objects.get(organization=org, id=booking_id)
            booking_services = BookingService.objects.filter(booking=booking)
            b_services = []  # all the services in a booking
            bs_total = 0
            for bs in booking_services:
                s = {
                    "booking_service_id": bs.id,
                    "title": None,
                    "beautician": None,
                    "ttl": None,
                    "pos": None,
                    "status": "Not Started",
                    "amount": None,
                    "amount_display": None,
                }

                if bs.service:
                    time_ = ""
                    ttl_hrs = bs.service.ttl_hrs or 0
                    ttl_min = bs.service.ttl_min or 0

                    if ttl_hrs > 0:
                        time_ = f"{ttl_hrs} {'hrs ' if ttl_hrs > 1 else 'hr '}"

                    if ttl_min > 0:
                        time_ += f"{ttl_min} {'mins' if ttl_min > 1 else 'min'}"

                    s["ttl"] = time_ or None
                    s["title"] = bs.service.title

                if bs.beautician:
                    s["beautician"] = bs.beautician.linked_user.first_name

                pos_object = Pos.objects.filter(pk=bs.pos_id).first()
                if pos_object:
                    s_pos = {"id": pos_object.id, "title": pos_object.title}
                    s["pos"] = s_pos

                status_object = bs.status
                if status_object:
                    s["status"] = status_object.title

                bs_total += bs.subtotal
                s["amount"] = bs.subtotal
                s["amount_display"] = get_amount_with_currency_code(bs.subtotal)

                b_services.append(s)

            total = bs_total
            taxes = []
            taxe_rates = get_tax_settings(org_id=org.id)
            for tax in taxe_rates:
                tax_amount = round(
                    (convert_string_to_float(tax["value"]) * bs_total) / 100, 2
                )
                total += tax_amount
                taxes.append(
                    {
                        "key": tax["key"],
                        "value": f"{tax['value']}%",
                        "amount": tax_amount,
                        "amount_display": get_amount_with_currency_code(tax_amount),
                    }
                )

            total = round(total, 2)

            org_poses = Pos.objects.filter(organization=org).values("id", "title")
            poses = [pos for pos in org_poses]

            customer = {
                "fullName": f"{booking.customer.first_name} {booking.customer.last_name}",
                "email": booking.customer.email,
                "phone": booking.customer.phone,
                "address": booking.customer.address,
                "profile_image": get_customer_file_URL(
                            booking.customer.id, "PROFILE_IMAGE", "MEDIA"
                        )
            }
            DS = {
                "booking_id": booking.id,
                "customer": jsonpickle.encode(customer, unpicklable=False),
                "booking_date": datetime.strftime(
                    booking.booking_date_time, "%Y-%m-%d %H:%M:%S%z"
                ),
                "services": b_services,
                "pos": poses,  # all of the pos
                "totals": {
                    "subtotal": bs_total,
                    "subtotal_display": get_amount_with_currency_code(bs_total),
                    "taxes": taxes,
                    "total": total,
                    "total_display": get_amount_with_currency_code(total),
                },
                "organization": {
                    # [To do] get from settings
                    "logo": "/assets/images/receipt/sample-logo.jpg",
                    "receipt_header": [
                        "My Company [San Fransisco]",
                        "Tel: +1 [650] 691-3277",
                        "GSTIN: 24BBBFF56798",
                        "https://example.com",
                        "Taking care of your looks is WORSHIP",
                        "---------------------",
                    ],
                    "staff": "Demo user",  # [To do] login user
                },
            }

            totalCount = 1

        if inKey == "booking_dataset":
            categories = Category.objects.filter(
                organization_id=org.id
            )
            service_categories = []
            for cat in categories:
                services = []
                for service in cat.services.all():
                    time_ = ""
                    ttl_hrs = service.ttl_hrs or 0
                    ttl_min = service.ttl_min or 0

                    if ttl_hrs > 0:
                        time_ = f"{ttl_hrs} {'hrs ' if ttl_hrs > 1 else 'hr '}"

                    if ttl_min > 0:
                        time_ += f"{ttl_min} {'mins' if ttl_min > 1 else 'min'}"

                    cost_price = round(service.cost_price, 2)
                    services.append(
                        {
                            "id": service.id,
                            "title": service.title,
                            "time": time_,
                            "price": cost_price,
                            "price_display": get_amount_with_currency_code(cost_price),
                        }
                    )

                service_categories.append(
                    {
                        "id": cat.id,
                        "category_title": cat.title,
                        "services": services,
                    }
                )

            beauticians = []
            for beautician in Beautician.objects.filter(
                organization_id=org.id
            ):
                beauticians.append(
                    {
                        "id": beautician.id,
                        "name": beautician.linked_user.first_name,
                        "image_url": get_user_file_URL(
                            beautician.linked_user.id, "PROFILE_IMAGE", "MEDIA"
                        ),
                    }
                )

            organization = {
                "id": org.id,
                "title": org.name,
                "address": "600 Portion Road, Ronkonkoma",
                "image_url": "/assets/images/cover_pic.png",
            }
            DS = {
                "services": service_categories,
                "resources": beauticians,
                "organization": organization,
            }
            totalCount = len(service_categories)

        d = SelectorDataModelType(totalCount=totalCount, rows=DS)
        return d


schema_selector = graphene.Schema(query=Query)
