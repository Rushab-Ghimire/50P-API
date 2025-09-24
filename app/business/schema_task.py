import graphene
from graphene_django import DjangoObjectType
from business.models import Task
from business.models.entity import Entity

class TaskType(DjangoObjectType):
  class Meta:
    model = Task
    fields = ("__all__")


class Query(graphene.ObjectType):
  task = graphene.List(TaskType)
  def resolve_task(self, info, **kwargs):
    return Task.objects.all()


class CreateTask(graphene.Mutation):
  class Arguments:
    title = graphene.String()
    description = graphene.String()
    business_id = graphene.Int()

  ok = graphene.Boolean()
  task = graphene.Field(TaskType)
  def mutate(self, info, title, description, business_id):
    try:
        business = Entity.objects.get(id = business_id)
    except Entity.DoesNotExist:
        raise Exception("Business does not exist")

    task = Task(title=title,
                description=description,
                business = business)
    task.save()
    return CreateTask(ok=True, task=task)


class DeleteTask(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
  ok = graphene.Boolean()
  def mutate(self, info, id):
    try:
        task = Task.objects.get(id)
    except Entity.DoesNotExist:
        raise Exception("Task does not exist")
    task.is_deleted = True
    return DeleteTask(ok=True)


class UpdateTask(graphene.Mutation):
  class Arguments:
    id = graphene.Int()
    title = graphene.String()
    description = graphene.String()

  ok = graphene.Boolean()
  task = graphene.Field(TaskType)

  def mutate(self, info, id, title, description, business_id):
    try:
        task = Task.objects.get(pk = id)
    except Entity.DoesNotExist:
        raise Exception("Task does not exist")

    try:
        business = Entity.objects.get(id = business_id)
    except Entity.DoesNotExist:
        raise Exception("Business does not exist")

    task.title = title
    task.description = description
    task.business = business
    task.save()
    return UpdateTask(ok=True, task=task)

class Mutation(graphene.ObjectType):
  create_task = CreateTask.Field()
  delete_task = DeleteTask.Field()
  update_task = UpdateTask.Field()


schema_task = graphene.Schema(query=Query, mutation=Mutation)
