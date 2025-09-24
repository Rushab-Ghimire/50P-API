import graphene
from graphene_django import DjangoObjectType
from salon.models import Pos, EntityType, FloorPlan
from django.db.models import Q
from graphql_jwt.decorators import login_required


class PosType(DjangoObjectType):
    class Meta:
        model = Pos
        fields = ["id", "title", "entity_type", "floorplan", "position"]


class EntityTypeType(DjangoObjectType):
    class Meta:
        model = EntityType
        fields = ["id", "title"]


class FloorPlanType(DjangoObjectType):
    class Meta:
        model = FloorPlan
        fields = ["id", "title", "position"]


class PosDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(PosType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_pos = graphene.Field(
        PosDataModelType,
        floorplan_id=graphene.Int(),
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_pos_by_id = graphene.Field(PosType, id=graphene.Int())

    @login_required
    def resolve_salon_pos(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        floorplan_id = kwargs.get("floorplan_id")
        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        org = info.context.user.get_organization()

        qs = Pos.objects.filter(organization=org, floorplan_id=floorplan_id)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return PosDataModelType(totalCount=totalCount, rows=qs)

    @login_required
    def resolve_salon_pos_by_id(root, info, id):
        org = info.context.user.get_organization()
        return Pos.objects.get(pk=id, organization=org)


class CreateSalonPos(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        entity_type_id = graphene.Int()
        floorplan_id = graphene.Int()
        position = graphene.Int()

    ok = graphene.Boolean()
    pos = graphene.Field(PosType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        entity_type_id = kwargs.get("entity_type_id")
        entity_type = None
        if entity_type_id:
            try:
                entity_type = EntityType.objects.get(
                    pk=entity_type_id, organization=org
                )
            except EntityType.DoesNotExist:
                raise Exception("Entity Type does not exists")

        floorplan_id = kwargs.get("floorplan_id")
        floorplan = None
        if floorplan_id:
            try:
                floorplan = FloorPlan.objects.get(pk=floorplan_id, organization=org)
            except FloorPlan.DoesNotExist:
                raise Exception("Floor plan does not exists")

        item = Pos(
            title=kwargs.get("title"),
            entity_type=entity_type,
            floorplan=floorplan,
            position=kwargs.get("position", 0),
            organization=org,
            user=session_user,
        )

        item.save()
        return CreateSalonPos(ok=True, pos=item)


class DeleteSalonPos(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        org = info.context.user.get_organization()

        try:
            item = Pos.objects.get(pk=id, organization=org)
        except Pos.DoesNotExist:
            raise Exception("Pos does not exist")

        item.is_deleted = True
        item.save()
        return DeleteSalonPos(ok=True)


class UpdateSalonPos(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        entity_type_id = graphene.Int()
        floorplan_id = graphene.Int()
        position = graphene.Int()

    ok = graphene.Boolean()
    pos = graphene.Field(PosType)

    @login_required
    def mutate(self, info, id, **kwargs):
        org = info.context.user.get_organization()

        try:
            item = Pos.objects.get(pk=id, organization=org)
        except Pos.DoesNotExist:
            raise Exception("Pos does not exist")

        entity_type_id = kwargs.get("entity_type_id")
        entity_type = None
        if entity_type_id:
            try:
                entity_type = EntityType.objects.get(
                    pk=entity_type_id, organization=org
                )
            except EntityType.DoesNotExist:
                raise Exception("Entity Type does not exists")

        floorplan_id = kwargs.get("floorplan_id")
        floorplan = None
        if floorplan_id:
            try:
                floorplan = FloorPlan.objects.get(pk=floorplan_id, organization=org)
            except FloorPlan.DoesNotExist:
                raise Exception("Floor plan does not exists")

        item.title = kwargs.get("title") or item.title
        item.entity_type = entity_type or item.entity_type
        item.floorplan = floorplan or item.floorplan
        item.position = kwargs.get("position") or item.position

        item.save()
        return UpdateSalonPos(ok=True, pos=item)


class Mutation(graphene.ObjectType):
    salon_pos_create = CreateSalonPos.Field()
    salon_pos_update = UpdateSalonPos.Field()
    salon_pos_delete = DeleteSalonPos.Field()


schema_salon_pos = graphene.Schema(query=Query, mutation=Mutation)
