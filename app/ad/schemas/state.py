import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import State, Country
from django.core.exceptions import ValidationError


class StateType(DjangoObjectType):
    class Meta:
        model = State
        fields = ["id", "name", "country", "abbr", "slug"]

class StateDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(StateType)

    class Meta:
        fields = ("totalCount", "rows")

class Query(graphene.ObjectType):
    all_states = graphene.Field(
        StateDataModelType, search=graphene.String(), country_id=graphene.Int(), first=graphene.Int(), skip=graphene.Int()
    )
    state_by_id = graphene.Field(StateType, id=graphene.Int())

    def resolve_all_states(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        country_id = kwargs.get("country_id")

        filter = Q()
        if search:
            filter = Q(name__icontains=search) | Q(abbr__icontains=search)

        if country_id:
            filter &= Q(country_id=country_id)

        qs = State.objects.filter(is_deleted=False).filter(filter)
        qs = qs.order_by("name")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return StateDataModelType(totalCount=totalCount, rows=qs)

    def resolve_state_by_id(self, info, id):
        try:
            return State.objects.get(pk=id)
        except State.DoesNotExist:
            return None


class CreateState(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        abbr = graphene.String(required=True)
        country_id = graphene.Int(required=True)

    state = graphene.Field(StateType)

    def mutate(self, info, name, abbr, country_id):
        slug = State.generate_slug(name)
        try:
            country = Country.objects.get(pk=country_id)
        except Country.DoesNotExist:
            raise ValidationError("Country not found")

        state = State(name=name, abbr=abbr, slug=slug, country=country)
        state.save()
        return CreateState(state=state)


class UpdateState(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        abbr = graphene.String()
        slug = graphene.String()
        country_id = graphene.Int()

    state = graphene.Field(StateType)

    def mutate(self, info, id, **kwargs):
        name = kwargs.get("name")
        abbr = kwargs.get("abbr")
        slug = kwargs.get("slug")
        country_id = kwargs.get("country_id")

        try:
            state = State.objects.get(pk=id)
        except State.DoesNotExist:
            raise ValidationError("State not found")

        if country_id:
            try:
                country = Country.objects.get(pk=country_id)
                state.country = country
            except Country.DoesNotExist:
                raise ValidationError("Country not found")

        state.name = name or state.name
        state.abbr = abbr or state.abbr
        if slug:
            state.slug = State.generate_slug(slug)

        state.save()
        return UpdateState(state=state)


class DeleteState(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            state = State.objects.get(pk=id)
        except State.DoesNotExist:
            raise ValidationError("State not found")

        state.is_deleted = True
        state.save()
        return DeleteState(ok=True)


class Mutation(graphene.ObjectType):
    state_create = CreateState.Field()
    state_update = UpdateState.Field()
    state_delete = DeleteState.Field()


state_schema = graphene.Schema(query=Query, mutation=Mutation)
