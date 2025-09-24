import graphene
from graphene_django import DjangoObjectType
from processflow.models import Process
from authtf.models import UIModelType
from django.db.models import Q

class ProcessType(DjangoObjectType):
  class Meta:
    model = Process
    fields = ("__all__")

class ProcessDataModelType(graphene.ObjectType):
  totalCount = graphene.Int()
  rows = graphene.List(ProcessType)
  class Meta:
    fields = ("totalCount", "rows")

class Query(graphene.ObjectType):
  process = graphene.Field(
      ProcessDataModelType,
      search=graphene.String(),
      first=graphene.Int(),
      skip=graphene.Int()
     )
  process_by_id = graphene.Field(ProcessType, id=graphene.Int())
  process_ui = graphene.Field(UIModelType)

  def resolve_process_ui(self, info):
    import json
    with open('./uiservice/ui/process/form.json', 'r') as f:
        o = json.load(f)
    d = UIModelType(title = 'process', ui = o)
    return d

  def resolve_process_by_id(root, info, id):
    return Process.objects.get(pk = id, is_deleted=False)

  def resolve_process(self, info, **kwargs):
    qs = Process.objects.filter(is_deleted = False)
    search = kwargs.get('search')
    skip = kwargs.get('skip')
    first = kwargs.get('first')
    if search:
        filter = (
            Q(title__icontains=search) |
            Q(api_endpoint__icontains=search)
        )
        qs = qs.filter(filter)
    totalCount = qs.count()
    if skip:
        qs = qs[skip:]

    if first:
        qs = qs[:first]

    d = ProcessDataModelType(totalCount = totalCount, rows = qs)
    return d

class CreateProcess(graphene.Mutation):
  class Arguments:
    title = graphene.String()
    in_params = graphene.JSONString()
    api_endpoint = graphene.String()
    out_params = graphene.JSONString()

  ok = graphene.Boolean()
  process = graphene.Field(ProcessType)
  def mutate(self, info, title, in_params, api_endpoint, out_params):
    process = Process(
                            title=title,
                            in_params=in_params,
                            api_endpoint = api_endpoint,
                            out_params = out_params
                        )
    process.save()
    return CreateProcess(ok=True, process=process)


class DeleteProcess(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
  ok = graphene.Boolean()
  def mutate(self, info, id):
    try:
        process = Process.objects.get(id)
    except Process.DoesNotExist:
        raise Exception("Process does not exist")
    process.is_deleted = True
    return DeleteProcess(ok=True)


class UpdateProcess(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
    title = graphene.String()
    in_params = graphene.JSONString()
    api_endpoint = graphene.String()
    out_params = graphene.JSONString()

  ok = graphene.Boolean()
  process = graphene.Field(ProcessType)



  def mutate(self, info, id, title, in_params, api_endpoint, out_params):

    try:
        process = Process.objects.get(pk = id)
    except Process.DoesNotExist:
        raise Exception("Process does not exist")

    process.title=title
    process.in_params=in_params
    process.api_endpoint = api_endpoint
    process.out_params = out_params
    process.save()
    return UpdateProcess(ok=True, process=process)

class Mutation(graphene.ObjectType):
  create_process = CreateProcess.Field()
  delete_process = DeleteProcess.Field()
  update_process = UpdateProcess.Field()


schema_process = graphene.Schema(query=Query, mutation=Mutation)
