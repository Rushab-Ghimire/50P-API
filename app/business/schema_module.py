import graphene
from graphene_django import DjangoObjectType
from business.models import Module, Quicklink
from authtf.models import UIModelType
from django.db.models import Q
from slugify import slugify

class QuicklinkType(DjangoObjectType):
  class Meta:
    model = Quicklink
    fields = ("__all__")

class ModuleType(DjangoObjectType):
  class Meta:
    model = Module
    fields = ("__all__")

class ModuleDataModelType(graphene.ObjectType):
  totalCount = graphene.Int()
  rows = graphene.List(ModuleType)
  class Meta:
    fields = ("totalCount", "rows")

class Query(graphene.ObjectType):
  module = graphene.Field(
      ModuleDataModelType,
      search=graphene.String(),
      first=graphene.Int(),
      skip=graphene.Int()
     )
  module_by_id = graphene.Field(ModuleType, id=graphene.Int())
  module_ui = graphene.Field(UIModelType)

  def resolve_module(self, info, **kwargs):
    qs = Module.objects.filter(is_deleted = False)
    search = kwargs.get('search')
    skip = kwargs.get('skip')
    first = kwargs.get('first')
    if search:
        filter = (
            Q(title__icontains=search) |
            Q(route__icontains=search) |
            Q(slug__icontains=search)
        )
        qs = qs.filter(filter)

    qs = qs.order_by("-modified_date")
    totalCount = qs.count()
    if skip:
        qs = qs[skip:]

    if first:
        qs = qs[:first]

    d = ModuleDataModelType(totalCount = totalCount, rows = qs)
    return d


  def resolve_contact_ui(self, info):
    import json
    with open('./uiservice/ui/module/form.json', 'r') as f:
        o = json.load(f)
    d = UIModelType(title = 'module', ui = o)
    return d

  def resolve_module_by_id(root, info, id):
    return Module.objects.get(pk = id, is_deleted=False)

class CreateModule(graphene.Mutation):
  class Arguments:
    title = graphene.String(required=True)
    icon = graphene.String()
    description = graphene.String()
    route = graphene.String(required=True)

  ok = graphene.Boolean()
  module = graphene.Field(ModuleType)
  def mutate(self, info, title, icon, description, route, **kwargs):
    module = Module( title=title,
                      icon=icon,
                      description=description,
                      route = route,
                      slug = slugify(title)
                      )
    module.save()
    return CreateModule(ok=True, module=module)

class DeleteModule(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
  ok = graphene.Boolean()
  def mutate(self, info, id):
    module = Module.objects.get(pk=id)
    module.is_deleted = True
    module.save();
    return DeleteModule(ok=True)

class UpdateModule(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
    title = graphene.String(required=True)
    icon = graphene.String()
    description = graphene.String()
    route = graphene.String(required=True)

  ok = graphene.Boolean()
  module = graphene.Field(ModuleType)

  def mutate(self, info, id, title, icon, description, route, **kwargs):
    module = Module.objects.get(pk = id)
    module.title = title
    module.icon = icon
    module.description = description
    module.route = route
    module.slug = slugify(title)
    module.save()
    return UpdateModule(ok=True, module=module)


class AddQuicklink(graphene.Mutation):
  class Arguments:
    user_id = graphene.Int()
    module_id = graphene.Int()

  ok = graphene.Boolean()
  quicklink = graphene.Field(QuicklinkType)
  def mutate(self, info, user_id, module_id, **kwargs):
    quicklink = Quicklink(
                        user_id = user_id,
                        module_id = module_id
                      )
    quicklink.save()
    return AddQuicklink(ok=True, quicklink=quicklink)

class DeleteQuicklink(graphene.Mutation):
  class Arguments:
    user_id = graphene.Int()
    module_id = graphene.Int()

  ok = graphene.Boolean()
  def mutate(self, info, user_id, module_id, **kwargs):
    quicklink = Quicklink.get(user_id = user_id, module_id = module_id)
    quicklink.remove()
    return DeleteQuicklink(ok=True)

class Mutation(graphene.ObjectType):
  create_module = CreateModule.Field()
  delete_module = DeleteModule.Field()
  update_module = UpdateModule.Field()
  add_quicklink = AddQuicklink.Field()
  delete_quicklink = DeleteQuicklink.Field()


schema_module = graphene.Schema(query=Query, mutation=Mutation)
