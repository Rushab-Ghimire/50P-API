import graphene
from graphene_django import DjangoObjectType
from business.models import Entity
from authtf.models import UIModelType
from django.db.models import Q
from pubsub.consumer import PubSubBroadcaster

class BusinessType(DjangoObjectType):
  class Meta:
    model = Entity
    fields = ("__all__")

class BusinessDataModelType(graphene.ObjectType):
  totalCount = graphene.Int()
  rows = graphene.List(BusinessType)
  class Meta:
    fields = ("totalCount", "rows")

class Query(graphene.ObjectType):
  business = graphene.Field(
      BusinessDataModelType,
      search=graphene.String(),
      first=graphene.Int(),
      skip=graphene.Int()
     )
  business_by_id = graphene.Field(BusinessType, id=graphene.Int())
  business_ui = graphene.Field(UIModelType)

  def resolve_business(self, info, **kwargs):
    qs = Entity.objects.filter(is_deleted = False)
    search = kwargs.get('search')
    skip = kwargs.get('skip')
    first = kwargs.get('first')
    if search:
        filter = (
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
        qs = qs.filter(filter)

    qs = qs.order_by("-modified_date")
    totalCount = qs.count()
    if skip:
        qs = qs[skip:]

    if first:
        qs = qs[:first]

    d = BusinessDataModelType(totalCount = totalCount, rows = qs)
    return d


  def resolve_business_ui(self, info):
    import json
    with open('./uiservice/ui/business/form.json', 'r') as f:
        o = json.load(f)
    d = UIModelType(title = 'business', ui = o)
    return d

  def resolve_business_by_id(root, info, id):
    return Entity.objects.get(pk = id, is_deleted=False)

class CreateBusiness(graphene.Mutation):
  class Arguments:
    title = graphene.String()
    description = graphene.String()

  ok = graphene.Boolean()
  business = graphene.Field(BusinessType)
  def mutate(self, info, title, description):
    business = Entity(title=title, description=description)
    business.save()
    return CreateBusiness(ok=True, business=business)

class DeleteBusiness(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
  ok = graphene.Boolean()
  def mutate(self, info, id):
    business = Entity.objects.get(pk=id)
    business.is_deleted = True
    business.save()
    return DeleteBusiness(ok=True)


class UpdateBusiness(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
    title = graphene.String()
    description = graphene.String()

  ok = graphene.Boolean()
  business = graphene.Field(BusinessType)

  def mutate(self, info, id, title, description):
    business = Entity.objects.get(pk = id)
    business.title = title
    business.description = description
    business.save()
    return UpdateBusiness(ok=True, business=business)



class Mutation(graphene.ObjectType):
  create_business = CreateBusiness.Field()
  delete_business = DeleteBusiness.Field()
  update_business = UpdateBusiness.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
