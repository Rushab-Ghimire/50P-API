import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from salon.models import (
    FloorPlan,
)

from graphql_jwt.decorators import login_required

class FloorPlanType(DjangoObjectType):
    class Meta:
        model = FloorPlan
        fields = ["id", "title", "position"]


class FloorPlanDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(FloorPlanType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_floor_plan = graphene.Field(
        FloorPlanDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_floor_plan_by_id = graphene.Field(FloorPlanType, id=graphene.Int())

    @login_required
    def resolve_salon_floor_plan(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter=Q()
        if search:
            filter = Q(title__icontains=search)

        org = info.context.user.get_organization()

        qs = FloorPlan.objects.filter(organization=org)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return FloorPlanDataModelType(totalCount=totalCount, rows=qs)

    def resolve_salon_floor_plan_by_id(root, info, id):
        return FloorPlan.objects.get(pk=id)


class CreateSalonFloorPlan(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        position = graphene.Int()

    ok = graphene.Boolean()
    floor_plan = graphene.Field(FloorPlanType)

    @login_required
    def mutate(self, info, title, position):
        session_user = info.context.user
        org = session_user.get_organization()

        item = FloorPlan(title=title, position=position, organization=org, user=session_user)
        item.save()
        return CreateSalonFloorPlan(ok=True, floor_plan=item)


class DeleteSalonFloorPlan(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        org = info.context.user.get_organization()
        try:
            item = FloorPlan.objects.get(pk=id, organization=org)
        except FloorPlan.DoesNotExist:
            raise Exception("Floor Plan does not exist")

        item.is_deleted = True
        item.save()
        return DeleteSalonFloorPlan(ok=True)


class UpdateSalonFloorPlan(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        title = graphene.String()
        position = graphene.Int()

    ok = graphene.Boolean()
    floor_plan = graphene.Field(FloorPlanType)

    @login_required
    def mutate(self, info, id, title, position):
        org = info.context.user.get_organization()
        try:
            item = FloorPlan.objects.get(pk=id, organization=org)
        except FloorPlan.DoesNotExist:
            raise Exception("Floor Plan does not exist")

        item.title = title
        item.position = position
        item.save()
        return UpdateSalonFloorPlan(ok=True, floor_plan=item)


class Mutation(graphene.ObjectType):
    salon_floor_plan_create = CreateSalonFloorPlan.Field()
    salon_floor_plan_update = UpdateSalonFloorPlan.Field()
    salon_floor_plan_delete = DeleteSalonFloorPlan.Field()


schema_salon_floor_plan = graphene.Schema(query=Query, mutation=Mutation)
