import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models.country import Country
from django.core.exceptions import ValidationError


class CountryType(DjangoObjectType):
    class Meta:
        model = Country
        fields = ["id", "name", "abbr", "slug"]

class CountryDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(CountryType)

    class Meta:
        fields = ("totalCount", "rows")

class Query(graphene.ObjectType):
    all_countries = graphene.Field(
        CountryDataModelType, search=graphene.String(), first=graphene.Int(), skip=graphene.Int()
    )
    country_by_id = graphene.Field(CountryType, id=graphene.Int())

    def resolve_all_countries(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q()
        if search:
            filter = Q(name__icontains=search) | Q(abbr__icontains=search)

        qs = Country.objects.filter(is_deleted=False).filter(filter)
        qs = qs.order_by("name")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return CountryDataModelType(totalCount=totalCount, rows=qs)

    def resolve_country_by_id(self, info, id):
        try:
            return Country.objects.get(pk=id)
        except Country.DoesNotExist:
            return None


class CreateCountry(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        abbr = graphene.String(required=True)

    country = graphene.Field(CountryType)

    def mutate(self, info, name, abbr):
        slug = Country.generate_slug(name)
        country = Country(name=name, abbr=abbr, slug=slug)
        country.save()
        return CreateCountry(country=country)


class UpdateCountry(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        abbr = graphene.String()
        slug = graphene.String()

    country = graphene.Field(CountryType)

    def mutate(self, info, id, **kwargs):
        name = kwargs.get("name")
        abbr = kwargs.get("abbr")
        slug = kwargs.get("slug")

        try:
            country = Country.objects.get(pk=id)
        except Country.DoesNotExist:
            raise ValidationError("Country not found")

        country.name = name or country.name
        country.abbr = abbr or country.abbr
        if slug:
            country.slug = Country.generate_slug(slug)

        country.save()
        return UpdateCountry(country=country)


class DeleteCountry(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            country = Country.objects.get(pk=id)
        except Country.DoesNotExist:
            raise ValidationError("Country not found")

        country.is_deleted = True
        country.save()
        return DeleteCountry(ok=True)


class Mutation(graphene.ObjectType):
    country_create = CreateCountry.Field()
    country_update = UpdateCountry.Field()
    country_delete = DeleteCountry.Field()


country_schema = graphene.Schema(query=Query, mutation=Mutation)
