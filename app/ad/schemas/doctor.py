from core.utils import tf_utils
import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import Doctor, EducationTraining, ADUserFile, ADUserFileTypes
from ad.schemas.insurance_provider import InsuranceProviderType

class EducationTrainingType(DjangoObjectType):
    class Meta:
        model = EducationTraining
        fields = ["id", "title"]

class DoctorType(DjangoObjectType):
    education_training = graphene.List(EducationTrainingType)
    insurance_accepted = graphene.List(InsuranceProviderType)
    profile_pic = graphene.String()

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "slug",
            "specialization",
            "description",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "website",
            "phone",
            "lat",
            "lng",
            "timezone",
            "languages",
            "is_premium",
            "ethnicities",
            "genders",
        ]

    def resolve_education_training(self, info):
        return self.education_trainings.all()

    def resolve_insurance_accepted(self, info):
        return self.insurance_providers.all()

    def resolve_profile_pic(self, info):
        if self.user:
            uf = ADUserFile.objects.filter(key="PROFILE_IMAGE", linked_user=self.user).first()
            if uf and uf.unique_id:
                return tf_utils.get_ad_file_URL_by_unique_id(
                    uf.unique_id.lower(), ADUserFileTypes.MEDIA
                )

        return tf_utils.get_default_media_url()


class DoctorDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(DoctorType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    all_doctors = graphene.Field(
        DoctorDataModelType,
        keys = graphene.String(required=True),
        values = graphene.String(required=True),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    doctor_by_id = graphene.Field(DoctorType, id=graphene.Int())

    def resolve_all_doctors(self, info, keys, values, **kwargs):
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
                Q(name__icontains=search)
                | Q(specialization__title__icontains=search)
                | Q(address__icontains=search)
                | Q(city__name__icontains=search)
                | Q(state__name__icontains=search)
                | Q(country__name__icontains=search)
                #| Q(state__abbr__icontains=state_id)
                #| Q(postal_code__icontains=pCode)
            )
            if pCode != "":
                filter = filter & Q(postal_code__icontains=pCode)

            if speciality != None:
                filter &= Q(specialization__id__in=speciality)

            if language != None:
                filter &= Q(languages__id__in=language)

            if ethnicity != None:
                filter &= Q(ethnicities__id__in=ethnicity)

            if gender != None:
                filter &= Q(genders__id__in=gender)

            if insurance != None:
                filter &= Q(insurance_providers__id__in=insurance)

            print("filter11", filter)

            if state_id != "" and state_id != "All":
                filter = filter & Q(state__abbr__icontains=state_id)

            print("filter", filter)

        qs = Doctor.objects.filter(filter).distinct()
        qs = qs.order_by("-is_premium")
        #.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return DoctorDataModelType(totalCount=totalCount, rows=qs)

    def resolve_doctor_by_id(self, info, id):
        try:
            return Doctor.objects.get(pk=id)
        except Doctor.DoesNotExist:
            return None


doctor_schema = graphene.Schema(query=Query)
