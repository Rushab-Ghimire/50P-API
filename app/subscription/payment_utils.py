from chargebee import Chargebee, Filters
from django.conf import settings
from subscription.utils import *


class PaymentUtils:
    def __init__(self):
        self.cb_client = Chargebee(
            api_key=settings.CHARGEBEE_API_KEY, site=settings.CHARGEBEE_SITE
        )

    def get_chargebee_hosted_page_for_new_subscription(self, customer, plan_id):
        return self.cb_client.HostedPage.checkout_new_for_items(
            {
                "subscription_items": [
                    {
                        "item_price_id": plan_id,
                    }
                ],
                "customer": customer,
            }
        )

    def get_chargebee_hosted_page_for_update_subscription(
        self, subscription_id, plan_id, customer
    ):
        return self.cb_client.HostedPage.checkout_existing_for_items(
            {
                "subscription": {"id": subscription_id},
                "subscription_items": [
                    {
                        "item_price_id": plan_id,
                    }
                ],
                "customer": customer,
            }
        )

    def get_chargebee_hosted_page_to_manage_payment_sources(self, customer_id):
        response = self.cb_client.HostedPage.manage_payment_sources(
            {"customer": {"id": customer_id}}
        )
        return response.hosted_page.raw_data

    def get_subscriptions(self, params):
        return self.cb_client.Subscription.list(params=params)

    def get_subscription(self, subscription_id):
        return self.cb_client.Subscription.retrieve(subscription_id)

    def get_item_price(self, plan_item_id):
        return self.cb_client.ItemPrice.retrieve(plan_item_id)

    def create_customer(self, customer):
        return self.cb_client.Customer.create(customer)

    def get_customer_list(self, params=None):
        return self.cb_client.Customer.list(params)

    def get_customer(self, customer_id):
        return self.cb_client.Customer.retrieve(customer_id)

    def update_customer(self, customer_id, params):
        return self.cb_client.Customer.update(customer_id, params=params)

    def update_subscription(self, subscription_id, params):
        return self.cb_client.Subscription.update_for_items(
            subscription_id, params=params
        )

    def create_subscription(self, customer_id, params):
        return self.cb_client.Subscription.create_with_items(
            customer_id, params=params
        )

    def cancel_subscription(self, subscription_id, params):
        return self.cb_client.Subscription.cancel_for_items(subscription_id, params)

    def remove_scheduled_cancellation(self, subscription_id):
        return self.cb_client.Subscription.remove_scheduled_cancellation(
            subscription_id
        )

    def get_invoice_list(self, params):
        return self.cb_client.Invoice.list(params)

    def get_payment_source_list(self, params):
        return self.cb_client.PaymentSource.list(params)

    def get_current_subscription_for_user(self, user):
        chargebee_customer = user.chargebee.first()
        if not chargebee_customer:
            return None

        chargebee_subscription = chargebee_customer.subscriptions.first()

        if not chargebee_subscription:
            return None

        sub = self.get_subscription(chargebee_subscription.subscription_id)
        subscription = sub.subscription
        plan = None
        if subscription.subscription_items and subscription.subscription_items[0]:
            subscription_item = subscription.subscription_items[0]
            plan = {
                "id": subscription_item.item_price_id,
                "amount": subscription_item.amount,
            }

            plan_item = self.get_item_price(subscription_item.item_price_id)
            if plan_item:
                plan["name"] = plan_item.item_price.external_name

        res_sub = {
            "id": subscription.id,
            "current_term_start": format_timestamp_to_date_time(
                subscription.current_term_start
            ),
            "current_term_end": format_timestamp_to_date_time(
                subscription.current_term_end
            ),
            "billing_period_unit": subscription.billing_period_unit,
            "status": subscription.status,
            "plan": plan,
        }

        if subscription.status == "non_renewing":
            res_sub["cancelled_at"] = format_timestamp_to_date_time(
                subscription.cancelled_at
            )

        res_sub["auto_collection"] = subscription.auto_collection in [None, "on"]

        return res_sub

    def get_invoices_for_user(
        self,
        user,
    ):
        chargebee_customer = user.chargebee.first()
        if not chargebee_customer:
            return []

        response = self.get_invoice_list(
            {
                "customer_id[is]": chargebee_customer.customer_id,
                "limit": 100,
                "sort_by[desc]": "date",
                "amount_paid[gt]": 0,
            }
        )

        invoices = []
        for entry in response.list:
            invoice = entry.invoice
            invoices.append(
                {
                    "id": invoice.id,
                    "total": invoice.total,
                    "status": invoice.status,
                    "date": format_timestamp_to_date_time(invoice.date),
                }
            )

        return invoices

    def get_all_cards_for_customer(self, customer_id):
        customer = self.get_customer(customer_id).customer
        primary_payment_source_id = customer.primary_payment_source_id if customer.primary_payment_source_id else None

        entries = self.get_payment_source_list(
            {
                "limit": 100,
                "type[is]": "card",
                "customer_id[is]": customer_id,
            }
        )
        payment_sources = []
        for entry in entries.list:
            source = entry.payment_source.raw_data
            card = source.get("card")
            source_id = source.get("id")
            payment_sources.append(
                {
                    "id": source_id,
                    "is_primary_payment_source": primary_payment_source_id == source_id,
                    "card": {
                        "masked_number": card.get("masked_number"),
                        "brand": card.get("brand"),
                        "expiry_month": card.get("expiry_month"),
                        "expiry_year": card.get("expiry_year"),
                        "first_name": card.get("first_name", ""),
                        "last_name": card.get("last_name", ""),
                    },
                }
            )
        return payment_sources
