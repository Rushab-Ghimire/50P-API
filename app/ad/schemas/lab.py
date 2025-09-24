from core.utils import tf_utils
import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import Lab, Country, State, City, ADUserFileTypes, InsuranceProvider
from ad.schemas.insurance_provider import InsuranceProviderType
from graphql_jwt.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from organization.models import Organization
from authtf.models import Role
from django.apps import apps

class LabType(DjangoObjectType):
    insurance_providers = graphene.List(InsuranceProviderType)
    logo = graphene.String()

    class Meta:
        model = Lab
        fields = [
            "id",
            "title",
            "description",
            "address",
            "country",
            "state",
            "city",
            "lattitude",
            "longitude",
            "logo_uuid",
        ]

    def resolve_insurance_providers(self, info):
        return self.insurance_providers.all()

    def resolve_logo(self, info):
        if self.logo_uuid:
            return tf_utils.get_ad_file_URL_by_unique_id(
                self.logo_uuid, ADUserFileTypes.MEDIA
            )

        return tf_utils.get_default_media_url()


class LabDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(LabType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    labs = graphene.Field(
        LabDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    lab_by_id = graphene.Field(LabType, id=graphene.Int())

    all_labs = graphene.Field(
        LabDataModelType,
        keys = graphene.String(required=True),
        values = graphene.String(required=True),
        first=graphene.Int(),
        skip=graphene.Int(),
    )

    def resolve_all_labs(self, info, keys, values, **kwargs):
        #search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        keys = keys.split("|||")
        values = values.split("|||")

        inputDict = dict(zip(keys, values))
        filter = Q()
        if inputDict:
            search = inputDict.get("search", "")
            pCode = inputDict.get("zip-code", "")
            state_id = inputDict.get("location", "")


            filterDict = dict()

            advancedFilterParams = inputDict.get("advancedFilterParams", "")

            if advancedFilterParams != "":
                aFP = advancedFilterParams.split("@@")
                qVal = None
                for aFPval in aFP:
                    qVal = aFPval.split("-")
                    filterDict[qVal[0]] = qVal[1].split("~")
                    if filterDict[qVal[0]][0] == "":
                        del filterDict[qVal[0]]


            # print(filterDict)

            speciality = filterDict.get("speciality", None)
            language = filterDict.get("language", None)
            ethnicity = filterDict.get("ethnicity", None)
            gender = filterDict.get("gender", None)
            insurance = filterDict.get("insurance", None)
            if insurance == "":
                insurance = None

            print(speciality, language, insurance, state_id)

            filter = (
                Q(title__icontains=search)
                | Q(address__icontains=search)
                | Q(city__name__icontains=search)
                | Q(state__name__icontains=search)
                | Q(country__name__icontains=search)
                #| Q(state__abbr__icontains=state_id)
                #| Q(postal_code__icontains=pCode)
            )
            # if pCode != "":
            #     filter = filter & Q(postal_code__icontains=pCode)

            # if speciality != None:
            #     filter &= Q(specialization__id__in=speciality)

            # if language != None:
            #     filter &= Q(languages__id__in=language)

            # if ethnicity != None:
            #     filter &= Q(ethnicities__id__in=ethnicity)

            # if gender != None:
            #     filter &= Q(genders__id__in=gender)

            if insurance != None:
                filter &= Q(insurance_providers__id__in=insurance)

            print("filter11", filter)

            if state_id != "" and state_id != "All":
                filter = filter & Q(state__abbr__icontains=state_id)

            print("filter", filter)

        qs = Lab.objects.filter(filter).distinct()
        #qs = qs.order_by("-is_premium")
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return LabDataModelType(totalCount=totalCount, rows=qs)

    def resolve_labs(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        qs = Lab.objects.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return LabDataModelType(totalCount=totalCount, rows=qs)

    def resolve_lab_by_id(self, info, id):
        try:
            return Lab.objects.get(pk=id)
        except Lab.DoesNotExist:
            return None


def create_user_for_lab(lab):
    email = f"{lab.id}_lab@askdaysi.com"
    first_name = lab.title
    last_name = ""
    password = f"Pw$@ABC{lab.id}"
    provider = get_user_model().objects.create_user(
        email=email,
        is_active=True,
        is_staff=False,
        first_name=first_name,
        last_name=last_name,
        password=password,
    )

    organization = Organization.objects.filter(business__id=1).first()
    if organization:
        role = Role.objects.get(identifier="lab")
        UserOrganization = apps.get_model("authtf", "UserOrganization")
        user_organization, _ = UserOrganization.objects.get_or_create(
            user=provider, organization=organization
        )
        user_organization.role.add(role)

    lab.user = provider
    lab.save()

    return provider

class CreateLab(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        address = graphene.String()
        country_id = graphene.Int()
        state_id = graphene.Int()
        city_id = graphene.Int()
        lattitude = graphene.Float()
        longitude = graphene.Float()
        logo_uuid = graphene.String()
        insurance_provider_ids = graphene.String()

    lab = graphene.Field(LabType)

    @login_required
    def mutate(self, info, title, **kwargs):
        session_user = info.context.user

        title = title
        description = kwargs.get("description")
        address = kwargs.get("address")
        country = kwargs.get("country_id")
        state = kwargs.get("state_id")
        city = kwargs.get("city_id")
        lattitude = kwargs.get("lattitude")
        longitude = kwargs.get("longitude")
        logo_uuid = kwargs.get("logo_uuid")
        insurance_provider_ids = kwargs.get("insurance_provider_ids")

        if title is None or title.strip() == "":
            raise ValidationError("Title is required")

        if country:
            try:
                country = Country.objects.get(pk=country)
            except Country.DoesNotExist:
                raise ValidationError("Country does not exist")

        if state:
            try:
                state = State.objects.get(pk=state)
            except State.DoesNotExist:
                raise ValidationError("State does not exist")

        if city:
            try:
                city = City.objects.get(pk=city)
            except City.DoesNotExist:
                raise ValidationError("City does not exist")

        if insurance_provider_ids and insurance_provider_ids.strip() != "":
            insurance_provider_ids = [int(ip.strip()) for ip in insurance_provider_ids.split("~") if ip.strip()]
            insurance_providers = InsuranceProvider.objects.filter(id__in=insurance_provider_ids).values_list("id", flat=True)


        lab = Lab.objects.create(
            title=title,
            description=description,
            address=address,
            country=country,
            state=state,
            city=city,
            lattitude=lattitude,
            longitude=longitude,
            logo_uuid=logo_uuid,
            organization=session_user.get_organization(),
            user=session_user,
        )
        if insurance_providers:
            lab.insurance_providers.set(insurance_providers)

        create_user_for_lab(lab)

        return CreateLab(lab=lab)


class UpdateLab(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        address = graphene.String()
        country_id = graphene.Int()
        state_id = graphene.Int()
        city_id = graphene.Int()
        lattitude = graphene.Float()
        longitude = graphene.Float()
        logo_uuid = graphene.String()
        insurance_provider_ids = graphene.String()

    lab = graphene.Field(LabType)

    @login_required
    def mutate(self, info, id, **kwargs):
        try:
            item = Lab.objects.get(pk=id)
        except Lab.DoesNotExist:
            raise ValidationError("Lab does not exist")

        country = kwargs.get("country_id")
        state = kwargs.get("state_id")
        city = kwargs.get("city_id")
        insurance_provider_ids = kwargs.get("insurance_provider_ids")

        if country:
            try:
                country = Country.objects.get(pk=country)
            except Country.DoesNotExist:
                raise ValidationError("Country does not exist")

        if state:
            try:
                state = State.objects.get(pk=state)
            except State.DoesNotExist:
                raise ValidationError("State does not exist")

        if city:
            try:
                city = City.objects.get(pk=city)
            except City.DoesNotExist:
                raise ValidationError("City does not exist")

        if insurance_provider_ids and insurance_provider_ids.strip() != "":
            insurance_provider_ids = [int(ip.strip()) for ip in insurance_provider_ids.split("~") if ip.strip()]
            insurance_providers = InsuranceProvider.objects.filter(id__in=insurance_provider_ids).values_list("id", flat=True)
            item.insurance_providers.clear()
            item.insurance_providers.set(insurance_providers)

        item.title = kwargs.get("title", item.title)
        item.description = kwargs.get("description", item.description)
        item.address = kwargs.get("address", item.address)
        item.country = country or item.country
        item.state = state or item.state
        item.city = city or item.city
        item.lattitude = kwargs.get("lattitude", item.lattitude)
        item.longitude = kwargs.get("longitude", item.longitude)
        item.logo_uuid = kwargs.get("logo_uuid", item.logo_uuid)

        item.save(
            update_fields=[
                "title",
                "description",
                "address",
                "country_id",
                "state_id",
                "city_id",
                "lattitude",
                "longitude",
                "logo_uuid",
            ]
        )

        if item.user is None:
            create_user_for_lab(item)

        return UpdateLab(lab=item)


class DeleteLab(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    @login_required
    def mutate(self, info, id):
        item = Lab.objects.get(pk=id, user=info.context.user)
        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteLab(ok=True)


class Mutation(graphene.ObjectType):
    lab_add = CreateLab.Field()
    lab_update = UpdateLab.Field()
    lab_delete = DeleteLab.Field()


lab_schema = graphene.Schema(query=Query, mutation=Mutation)
