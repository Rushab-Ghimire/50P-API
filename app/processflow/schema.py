import graphene
from graphene_django import DjangoObjectType
from processflow.models import ProcessFlow
from authtf.models import UIModelType
from django.db.models import Q

class ProcessFlowType(DjangoObjectType):
  class Meta:
    model = ProcessFlow
    fields = ("__all__")

class DataModelType(graphene.ObjectType):
  totalCount = graphene.Int()
  rows = graphene.List(ProcessFlowType)
  class Meta:
    fields = ("totalCount", "rows")

class Query(graphene.ObjectType):
  processflow = graphene.Field(
      DataModelType,
      search=graphene.String(),
      first=graphene.Int(),
      skip=graphene.Int()
     )
  processflow_by_id = graphene.Field(ProcessFlowType, id=graphene.Int())
  processflow_ui = graphene.Field(UIModelType)

  def resolve_processflow_ui(self, info):
    import json
    with open('./uiservice/ui/processflow/form.json', 'r') as f:
        o = json.load(f)
    d = UIModelType(title = 'processflow', ui = o)
    return d

  def resolve_processflow_by_id(root, info, id):
    return ProcessFlow.objects.get(pk = id, is_deleted=False)

  def resolve_processflow(self, info, **kwargs):
    qs = ProcessFlow.objects.filter(is_deleted = False)
    search = kwargs.get('search')
    skip = kwargs.get('skip')
    first = kwargs.get('first')
    if search:
        filter = (
            Q(title__icontains=search) |
            Q(specification__icontains=search)
        )
        qs = qs.filter(filter)
    totalCount = qs.count()
    if skip:
        qs = qs[skip:]

    if first:
        qs = qs[:first]

    d = DataModelType(totalCount = totalCount, rows = qs)
    return d


class CreateProcessFlow(graphene.Mutation):
  class Arguments:
    title = graphene.String()
    specification = graphene.JSONString()

  ok = graphene.Boolean()
  processflow = graphene.Field(ProcessFlowType)
  def mutate(self, info, title, specification):
    processflow = ProcessFlow(
                            title=title,
                            specification=specification
                        )
    processflow.save()
    return CreateProcessFlow(ok=True, processflow=processflow)


class DeleteProcessFlow(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
  ok = graphene.Boolean()
  def mutate(self, info, id):
    try:
        processflow = ProcessFlow.objects.get(id)
    except ProcessFlow.DoesNotExist:
        raise Exception("ProcessFlow does not exist")
    processflow.is_deleted = True
    return DeleteProcessFlow(ok=True)


class UpdateProcessFlow(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
    title = graphene.String()
    specification = graphene.JSONString()

  ok = graphene.Boolean()
  processflow = graphene.Field(ProcessFlowType)

  def mutate(self, info, id, title, specification):
    try:
        processflow = ProcessFlow.objects.get(pk = id)
    except ProcessFlow.DoesNotExist:
        raise Exception("ProcessFlow does not exist")

    processflow.title=title
    processflow.specification=specification
    processflow.save()
    return UpdateProcessFlow(ok=True, processflow=processflow)

class Mutation(graphene.ObjectType):
  create_process_flow = CreateProcessFlow.Field()
  delete_process_flow = DeleteProcessFlow.Field()
  update_process_flow = UpdateProcessFlow.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
