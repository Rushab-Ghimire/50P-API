import graphene
import random
from ad.models import Doctor, City

class PopulateDataModelType(graphene.ObjectType):
    ok = graphene.Boolean()

    class Meta:
        fields = "ok"

def import_data_for_doctor():
    languages = [2, 3, 4, 5, 6, 7]
    insurance_providers = [1, 2, 3, 4, 5, 6]
    specializations = [1,2]
    # city_ids = [4049286, 4707894, 5391959, 4164138, 4185686]

    for doctor in Doctor.objects.all():
        rn_lang = random.randint(1, 3)
        lang_set = random.sample(languages, rn_lang)
        doctor.languages.clear()
        doctor.languages.set(lang_set)

        rn_ip = random.randint(1, 3)
        ip_set = random.sample(insurance_providers, rn_ip)
        doctor.insurance_providers.clear()
        doctor.insurance_providers.set(ip_set)

        rn_spe = random.randint(1,2)
        spe_set = random.sample(specializations, rn_spe)
        doctor.specialization.clear()
        doctor.specialization.set(spe_set)

        # city_id = random.sample(city_ids, 1)[0]
        # city = City.objects.select_related("state", "state__country").get(pk=city_id)

        # doctor.city = city
        # doctor.state = city.state
        # doctor.country = city.state.country

        doctor.save()

class Query(graphene.ObjectType):
    populated_doctor_data = graphene.Field(PopulateDataModelType)

    def resolve_populated_doctor_data(self, info):
        import_data_for_doctor()
        return PopulateDataModelType(ok=True)


populate_data_schema = graphene.Schema(query=Query)
