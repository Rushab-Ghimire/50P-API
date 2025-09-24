import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import City, State
from django.core.exceptions import ValidationError


class CityType(DjangoObjectType):
    class Meta:
        model = City
        fields = ["id", "name", "state", "slug", "lat", "lng"]


class CityDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(CityType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    all_cities = graphene.Field(
        CityDataModelType,
        search=graphene.String(),
        state_id=graphene.Int(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    city_by_id = graphene.Field(CityType, id=graphene.Int())

    def resolve_all_cities(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        state_id = kwargs.get("state_id")

        filter = Q()
        if search:
            filter = Q(name__icontains=search) | Q(abbr__icontains=search)

        if state_id:
            filter &= Q(state_id=state_id)

        qs = City.objects.filter(is_deleted=False).filter(filter)
        qs = qs.order_by("name")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return CityDataModelType(totalCount=totalCount, rows=qs)

    def resolve_city_by_id(self, info, id):
        try:
            return City.objects.get(pk=id)
        except City.DoesNotExist:
            return None


class CreateCity(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        state_id = graphene.Int(required=True)
        lat = graphene.Float()
        lng = graphene.Float()

    city = graphene.Field(CityType)

    def mutate(self, info, **kwargs):
        name = kwargs.get("name")
        state_id = kwargs.get("state_id")
        lat = kwargs.get("lat")
        lng = kwargs.get("lng")

        try:
            state = State.objects.get(pk=state_id)
        except State.DoesNotExist:
            raise ValidationError("State not found")

        slug = City.generate_slug(name)
        city = City.objects.create(
            name=name, slug=slug, lat=lat, lng=lng, state=state
        )
        return CreateCity(city=city)


class UpdateCity(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        slug = graphene.String()
        state_id = graphene.Int()
        lat = graphene.Float()
        lng = graphene.Float()

    city = graphene.Field(CityType)

    def mutate(self, info, id, **kwargs):
        name = kwargs.get("name")
        slug = kwargs.get("slug")
        state_id = kwargs.get("state_id")
        lat = kwargs.get("lat")
        lng = kwargs.get("lng")

        try:
            city = City.objects.get(pk=id)
        except City.DoesNotExist:
            raise ValidationError("City not found")

        if state_id:
            try:
                state = State.objects.get(pk=state_id)
                city.state = state
            except State.DoesNotExist:
                raise ValidationError("State not found")

        city.name = name or city.name
        if slug:
            city.slug = City.generate_slug(slug)
        city.lat = lat or city.lat
        city.lng = lng or city.lng

        city.save()
        return UpdateCity(city=city)


class DeleteCity(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            city = City.objects.get(pk=id)
        except City.DoesNotExist:
            raise ValidationError("City not found")

        city.is_deleted = True
        city.save()
        return DeleteCity(ok=True)


class Mutation(graphene.ObjectType):
    city_create = CreateCity.Field()
    city_update = UpdateCity.Field()
    city_delete = DeleteCity.Field()


city_schema = graphene.Schema(query=Query, mutation=Mutation)
