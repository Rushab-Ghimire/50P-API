import graphene
from graphql_jwt.decorators import login_required

from django.db.models import Q
from ad.models import *
import graphene
from graphene.types.json import JSONString
from graphql_jwt.decorators import login_required
from core.utils.tf_utils import get_ad_file_URL_by_unique_id, get_ad_user_file_URL


class ADSelectorDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.Field(JSONString)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    patient_profile = graphene.Field(ADSelectorDataModelType)
    provider_profile = graphene.Field(ADSelectorDataModelType)
    check_insurance = graphene.Field(
        ADSelectorDataModelType,
        insurance_provider=graphene.String(required=True),
        member_id=graphene.String(required=True),
        subscription_number=graphene.String(required=True),
    )

    ad_media = graphene.Field(
        graphene.String(),
        owner_id=graphene.Int(),
        owner_type=graphene.String(),
        key=graphene.String(),
    )
    ad_media_by_unique_id = graphene.Field(
        graphene.String(), unique_id=graphene.String()
    )

    ad_file = graphene.Field(
        graphene.String(),
        owner_id=graphene.Int(),
        owner_type=graphene.String(),
        key=graphene.String(),
    )
    ad_file_by_unique_id = graphene.Field(
        graphene.String(), unique_id=graphene.String()
    )

    def resolve_ad_file(root, info, owner_id, owner_type, key):
        return get_ad_user_file_URL(owner_id, key, "document")

    def resolve_ad_file_by_unique_id(root, info, unique_id):
        return get_ad_file_URL_by_unique_id(unique_id, "document")

    def resolve_ad_media(root, info, owner_id, owner_type, key):
        return get_ad_user_file_URL(owner_id, key, "media")

    def resolve_ad_media_by_unique_id(root, info, unique_id):
        return get_ad_file_URL_by_unique_id(unique_id, "media")

    def resolve_check_insurance(
        self, info, insurance_provider, member_id, subscription_number, **kwargs
    ):
        # print(insurance_provider, member_id, subscription_number)
        try:
            ip = InsuranceProvider.objects.get(pk=int(insurance_provider))
        except InsuranceProvider.DoesNotExist:
            DS = {"found": 0}
            d = ADSelectorDataModelType(totalCount=0, rows=DS)
            return d

        totalCount = 0
        filter = Q(insurance_provider=ip)

        qs = (
            InsuranceRecord.objects.filter(filter)
            .filter(member_id=member_id)
            .filter(subscription_number=subscription_number)
        )
        totalCount = qs.count()

        DS = {"found": totalCount}
        d = ADSelectorDataModelType(totalCount=totalCount, rows=DS)
        return d

    @login_required
    def resolve_patient_profile(self, info, **kwargs):
        session_user = info.context.user

        ref_code = ""
        try:
            referral_code = ReferralCode.objects.get(user=session_user)
            ref_code = referral_code.code
        except ReferralCode.DoesNotExist:
            pass

        uf = ADUserFile.objects.filter(key="PROFILE_IMAGE", linked_user=session_user).first()
        DS = {
            "id": session_user.id,
            "firstName": session_user.first_name,
            "lastName": session_user.last_name,
            "email": session_user.email,
            "phone": session_user.phone,
            "default_language": session_user.default_language_id,
            "default_ethnicity": session_user.default_ethnicity_id,
            "profile_pic_unique_id": "" if uf == None else uf.unique_id,
            "referral_code": ref_code,
        }

        totalCount = 1

        d = ADSelectorDataModelType(totalCount=totalCount, rows=DS)
        return d

    @login_required
    def resolve_provider_profile(self, info, **kwargs):
        session_user = info.context.user
        # print(session_user)

        ref_code = ""
        try:
            referral_code = ReferralCode.objects.get(user=session_user)
            ref_code = referral_code.code
        except ReferralCode.DoesNotExist:
            pass

        DS = {
            "id": session_user.id,
            "firstName": session_user.first_name,
            "lastName": session_user.last_name,
            "email": session_user.email,
            "phone": session_user.phone,
            "default_language": session_user.default_language_id,
            "default_ethnicity": session_user.default_ethnicity_id,
            "city_id": None,
            "state_id": None,
            "address": None,
            "description": None,
            "postal_code": None,
            "is_premium": False,
            "appointment_cost": 0,
            "provider": {},
            "profile_pic_unique_id": "",
            "referral_code": ref_code,
        }

        provider = {
            "education_training": [],
            "insurance_accepted": [],
            "languages": [],
            "specialization": [],
            "ethnicities": [],
            "genders": [],
        }
        doctor = session_user.doctor_set.first()
        if doctor:
            provider = {
                "education_training": list(
                    doctor.education_trainings.values("id", "title")
                ),
                "insurance_accepted": [
                    {
                        "id": ip.id,
                        "name": ip.name,
                        "logo": get_ad_file_URL_by_unique_id(ip.logo, ADUserFileTypes.MEDIA),
                        "location": ip.location,
                    }
                    for ip in doctor.insurance_providers.all()
                ],
                "languages": list(doctor.languages.values("id", "title")),
                "ethnicities": list(doctor.ethnicities.values("id", "title")),
                "genders": list(doctor.genders.values("id", "title")),
                "specialization": list(doctor.specialization.values("id", "title")),
            }

            DS["state_id"] = doctor.state_id
            DS["city_id"] = doctor.city_id
            DS["address"] = doctor.address
            DS["description"] = doctor.description
            DS["postal_code"] = doctor.postal_code
            DS["is_premium"] = doctor.is_premium
            DS["appointment_cost"] = doctor.appointment_cost
            DS["phone_official"] = doctor.phone_official

        uf = ADUserFile.objects.filter(key="PROFILE_IMAGE", linked_user=session_user).first()

        DS["provider"] = provider
        DS["profile_pic_unique_id"] = "" if uf == None else uf.unique_id,

        totalCount = 1

        d = ADSelectorDataModelType(totalCount=totalCount, rows=DS)
        return d


class UpdatePatientProfile(graphene.Mutation):
    class Arguments:
        keys = graphene.String(required=True)
        values = graphene.String(required=True)

    status = graphene.String()

    @login_required
    def mutate(self, info, keys, values, **kwargs):
        session_user = info.context.user
        keys = keys.split("|||")
        values = values.split("|||")
        inputDict = dict(zip(keys, values))

        session_user.first_name = inputDict.get("firstName", session_user.first_name)
        session_user.last_name = inputDict.get("lastName", session_user.last_name)
        session_user.email = inputDict.get("email", session_user.email)
        session_user.phone = inputDict.get("phone", session_user.phone)

        default_language = inputDict.get("default_language", "")
        if default_language != "":
            language = Language.objects.get(pk=default_language)
            session_user.default_language = language
            session_user.save(update_fields=["first_name", "last_name", "email", "phone", "default_language"])
        else:
            session_user.save(update_fields=["first_name", "last_name", "email", "phone"])

        default_ethnicity = inputDict.get("default_ethnicity", "")
        if default_ethnicity != "":
            try:
                ethnicity = Ethnicity.objects.get(pk=default_ethnicity)
                session_user.default_ethnicity = ethnicity
                session_user.save(update_fields=["default_ethnicity"])
            except Ethnicity.DoesNotExist:
                pass

        unique_id = inputDict.get("unique_id", "")
        if unique_id != "":
            uf = ADUserFile.objects.filter(
                key=ADUserFileKeys.PROFILE_IMAGE, linked_user=session_user
            ).first()
            if uf:
                uf.unique_id = unique_id
                uf.save(update_fields=["unique_id"])
            else:
                uf = ADUserFile(
                    key=ADUserFileKeys.PROFILE_IMAGE,
                    unique_id=unique_id,
                    linked_user=session_user,
                    user=session_user,
                    organization=session_user.get_organization(),
                )
                uf.save()

        return UpdatePatientProfile(status="ok")


class UpdateProviderProfile(graphene.Mutation):
    class Arguments:
        keys = graphene.String(required=True)
        values = graphene.String(required=True)

    status = graphene.String()

    def mutate(self, info, keys, values, **kwargs):
        session_user = info.context.user
        keys = keys.split("|||")
        values = values.split("|||")
        inputDict = dict(zip(keys, values))

        #print("inputDict", inputDict)

        session_user.first_name = inputDict.get("firstName", session_user.first_name)
        session_user.last_name = inputDict.get("lastName", session_user.last_name)
        session_user.email = inputDict.get("email", session_user.email)
        #session_user.phone = inputDict.get("phone", session_user.phone)

        user_phone = inputDict.get("phone", "")
        if user_phone.strip() != "":
            session_user.phone = user_phone

        default_language = inputDict.get("default_language", "")
        if default_language != "":
            language = Language.objects.get(pk=default_language)
            session_user.default_language = language

        doctor = session_user.doctor_set.first()
        create_new_doctor = False
        if doctor is None:
            doctor = Doctor(user=session_user, organization=session_user.get_organization())
            create_new_doctor = True

        doctor_name = inputDict.get("name", f"{session_user.first_name} {session_user.last_name}")
        if doctor_name != "" and doctor.name != doctor_name:
            doctor.name = doctor_name
            doctor.slug = Doctor.generate_slug(doctor_name)

        doctor.description = inputDict.get("description", doctor.description)
        doctor.address = inputDict.get("address", doctor.address)
        doctor.postal_code = inputDict.get("postal_code", doctor.postal_code)

        is_premium = int(inputDict.get("is_premium", "0"))
        doctor.is_premium = bool(is_premium)

        doctor.appointment_cost = round(float(inputDict.get("appointment_cost", doctor.appointment_cost)), 2)
        doctor.phone = inputDict.get("phone", doctor.phone)
        doctor.phone_official = inputDict.get("phone_official", doctor.phone_official)

        if create_new_doctor:
            doctor.save()

        session_user.save()

        languages = inputDict.get("languages", "").strip()
        if languages != "":
            language_lists = [int(et.strip()) for et in languages.split("~") if et.strip()]
            if language_lists:
                doctor.languages.clear()
                doctor.languages.set(language_lists)

        ethnicities = inputDict.get("ethnicities", "").strip()
        if ethnicities != "":
            ethnicity_lists = [int(et.strip()) for et in ethnicities.split("~") if et.strip()]
            if ethnicity_lists:
                doctor.ethnicities.clear()
                doctor.ethnicities.set(ethnicity_lists)

        genders = inputDict.get("genders", "").strip()
        if genders != "":
            gender_lists = [int(et.strip()) for et in genders.split("~") if et.strip()]
            if gender_lists:
                doctor.genders.clear()
                doctor.genders.set(gender_lists)

        accepted_insurances = inputDict.get("accepted_insurances", None)
        if accepted_insurances != "":
            accepted_insurance_lists = [int(et.strip()) for et in accepted_insurances.split("~") if et.strip()]
            if accepted_insurance_lists:
                doctor.insurance_providers.clear()
                doctor.insurance_providers.set(accepted_insurance_lists)

        specializations = inputDict.get("specializations", None)
        if specializations != "":
            specialization_lists = [int(et.strip()) for et in specializations.split("~") if et.strip()]
            if specialization_lists:
                doctor.specialization.clear()
                doctor.specialization.set(specialization_lists)

        city_id = inputDict.get("city_id", None)
        if city_id:
            try:
                city = City.objects.select_related("state", "state__country").get(pk=city_id)
                doctor.city = city
                doctor.state = city.state
                doctor.country = city.state.country
            except City.DoesNotExist:
                pass

        doctor.save()

        education_trainings = inputDict.get("education_training", "").strip()
        if education_trainings != "":
            education_training_lists = [EducationTraining(title=et.strip(), doctor=doctor) for et in education_trainings.split("~") if et.strip()]
            if education_training_lists:
                doctor.education_trainings.all().delete()
                EducationTraining.objects.bulk_create(education_training_lists)

        unique_id = inputDict.get("unique_id", "")
        if unique_id != "":
            uf = ADUserFile.objects.filter(
                key=ADUserFileKeys.PROFILE_IMAGE, linked_user=session_user
            ).first()
            if uf:
                uf.unique_id = unique_id
                uf.save(update_fields=["unique_id"])
            else:
                uf = ADUserFile(
                    key=ADUserFileKeys.PROFILE_IMAGE,
                    unique_id=unique_id,
                    linked_user=session_user,
                    user=session_user,
                    organization=session_user.get_organization(),
                )
                uf.save()

        return UpdateProviderProfile(status="ok")


class Mutation(graphene.ObjectType):
    update_patient_profile = UpdatePatientProfile.Field()
    update_provider_profile = UpdateProviderProfile.Field()


schema_ad_micro_tasks = graphene.Schema(query=Query, mutation=Mutation)
