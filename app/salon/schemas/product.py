import graphene
from graphene_django import DjangoObjectType
from salon.models import Product, Category
from organization.models import Organization
from django.conf import settings
from django.db.models import Q
from graphql_jwt.decorators import login_required


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ["id", "title", "cost_price", "sales_price", "category"]

class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ["id", "title"]

class ProductDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(ProductType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_product = graphene.Field(
        ProductDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_product_by_id = graphene.Field(ProductType, id=graphene.Int())

    @login_required
    def resolve_salon_product(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        org = info.context.user.get_organization()

        qs = Product.objects.filter(organization=org)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return ProductDataModelType(totalCount=totalCount, rows=qs)

    def resolve_salon_product_by_id(root, info, id):
        return Product.objects.get(pk=id)


class CreateSalonProduct(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        sales_price = graphene.Float()
        cost_price = graphene.Float()
        category_id = graphene.Int()

    ok = graphene.Boolean()
    product = graphene.Field(ProductType)

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

        item = Product(
            title=kwargs.get("title"),
            sales_price=kwargs.get("sales_price", 0.0),
            cost_price=kwargs.get("cost_price", 0.0),
            category=category,
            organization=org,
            user=session_user,
        )

        item.save()
        return CreateSalonProduct(ok=True, product=item)


class DeleteSalonProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        org = info.context.user.get_organization()
        try:
            item = Product.objects.get(pk=id, organization=org)
        except Product.DoesNotExist:
            raise Exception("Product does not exist")

        item.is_deleted = True
        item.save()
        return DeleteSalonProduct(ok=True)


class UpdateSalonProduct(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        sales_price = graphene.Float()
        cost_price = graphene.Float()
        category_id = graphene.Int()

    ok = graphene.Boolean()
    product = graphene.Field(ProductType)

    @login_required
    def mutate(self, info, id, **kwargs):
        org = info.context.user.get_organization()

        try:
            item = Product.objects.get(pk=id, organization=org)
        except Product.DoesNotExist:
            raise Exception("Product does not exists")

        category_id = kwargs.get("category_id")
        if category_id:
            try:
                category = Category.objects.get(pk=category_id, organization=org)
                item.category = category
            except Category.DoesNotExist:
                raise Exception("Category does not exists")

        item.title = kwargs.get("title") or item.title
        item.sales_price = kwargs.get("sales_price") or item.sales_price
        item.cost_price = kwargs.get("cost_price") or item.cost_price

        item.save()
        return UpdateSalonProduct(ok=True, product=item)


class Mutation(graphene.ObjectType):
    salon_product_create = CreateSalonProduct.Field()
    salon_product_update = UpdateSalonProduct.Field()
    salon_product_delete = DeleteSalonProduct.Field()


schema_salon_product = graphene.Schema(query=Query, mutation=Mutation)
