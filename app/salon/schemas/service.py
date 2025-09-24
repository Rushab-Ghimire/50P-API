import graphene
from graphene_django import DjangoObjectType
from salon.models import Service, Category
from django.db.models import Q
from graphql_jwt.decorators import login_required


class ServiceType(DjangoObjectType):
    class Meta:
        model = Service
        fields = ["id", "title", "code", "sales_price", "cost_price", "category", "ttl_hrs", "ttl_min"]


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ["id", "title"]


class ServiceDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(ServiceType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_service = graphene.Field(
        ServiceDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_service_by_id = graphene.Field(ServiceType, id=graphene.Int())

    @login_required
    def resolve_salon_service(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = Q(title__icontains=search) | Q(code__icontains=search)

        org = info.context.user.get_organization()

        qs = Service.objects.filter(organization=org)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return ServiceDataModelType(totalCount=totalCount, rows=qs)

    def resolve_salon_service_by_id(root, info, id):
        return Service.objects.get(pk=id)


class CreateSalonService(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        code = graphene.String(required=True)
        sales_price = graphene.Float()
        cost_price = graphene.Float()
        category_id = graphene.Int()
        ttl_hrs = graphene.Int()
        ttl_min = graphene.Int()

    ok = graphene.Boolean()
    service = graphene.Field(ServiceType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        category_id = kwargs.get("category_id")
        category = None
        if category_id:
            try:
                category = Category.objects.get(pk=category_id, organization=org)
            except Category.DoesNotExist:
                raise Exception("Category does not exists")

        item = Service(
            title=kwargs.get("title"),
            code=kwargs.get("code"),
            sales_price=kwargs.get("sales_price", 0.0),
            cost_price=kwargs.get("cost_price", 0.0),
            category=category,
            ttl_hrs=kwargs.get("ttl_hrs", 0),
            ttl_min=kwargs.get("ttl_min", 0),
            organization=org,
            user=session_user,
        )

        item.save()
        return CreateSalonService(ok=True, service=item)


class DeleteSalonService(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            item = Service.objects.get(pk=id)
        except Service.DoesNotExist:
            raise Exception("Service does not exist")

        item.is_deleted = True
        item.save()
        return DeleteSalonService(ok=True)


class UpdateSalonService(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        code = graphene.String()
        sales_price = graphene.Float()
        cost_price = graphene.Float()
        category_id = graphene.Int()
        ttl_hrs = graphene.Int()
        ttl_min = graphene.Int()

    ok = graphene.Boolean()
    service = graphene.Field(ServiceType)

    @login_required
    def mutate(self, info, id, **kwargs):
        org = info.context.user.get_organization()

        try:
            item = Service.objects.get(pk=id, organization=org)
        except Service.DoesNotExist:
            raise Exception("Service does not exist")

        category_id = kwargs.get("category_id")
        if category_id:
            try:
                category = Category.objects.get(pk=category_id, organization=org)
                item.category = category
            except Category.DoesNotExist:
                raise Exception("Category does not exists")

        item.title = kwargs.get("title") or item.title
        item.code = kwargs.get("code") or item.code
        item.sales_price = kwargs.get("sales_price") or item.sales_price
        item.cost_price = kwargs.get("cost_price") or item.cost_price
        item.ttl_hrs = kwargs.get("ttl_hrs") or item.ttl_hrs
        item.ttl_min = kwargs.get("ttl_min") or item.ttl_min

        item.save()
        return UpdateSalonService(ok=True, service=item)


class Mutation(graphene.ObjectType):
    salon_service_create = CreateSalonService.Field()
    salon_service_update = UpdateSalonService.Field()
    salon_service_delete = DeleteSalonService.Field()


schema_salon_service = graphene.Schema(query=Query, mutation=Mutation)
