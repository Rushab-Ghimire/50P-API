import graphene
from graphene_django import DjangoObjectType
from salon.models import (
    Queue, CustomerSalon
)
from organization.models import Organization
from django.conf import settings
from django.db.models import Q
from datetime import datetime
from graphql_jwt.decorators import login_required


class QueueType(DjangoObjectType):
    class Meta:
        model = Queue
        fields = "__all__"

class QueueDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(QueueType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    salon_queue = graphene.Field(
        QueueDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    salon_queue_by_id = graphene.Field(QueueType, id=graphene.Int())

    @login_required
    def resolve_salon_queue(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = (
                Q(customer__first_name__icontains=search)
                | Q(customer__last_name__icontains=search)
                | Q(customer__email__icontains=search)
                | Q(customer__phone__icontains=search)
            )

        org = info.context.user.get_organization()

        qs = Queue.objects.filter(organization=org, booking=None)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return QueueDataModelType(totalCount=totalCount, rows=qs)

    def resolve_salon_queue_by_id(root, info, id):
        return Queue.objects.get(pk=id)


class CreateSalonQueue(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=True)
        queue_date_time = graphene.String()
        note = graphene.String(required=True)

    ok = graphene.Boolean()
    queue = graphene.Field(QueueDataModelType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        queue_date_time = kwargs.get("queue_date_time")
        note = kwargs.get("note")
        item = CustomerSalon(
            first_name=kwargs.get("first_name"),
            last_name=kwargs.get("last_name"),
            email=kwargs.get("email"),
            phone=kwargs.get("phone"),
            organization=org,
            user=session_user,
        )
        item.save()
        q_item = Queue(
            customer = item,
            queue_date_time = queue_date_time,
            note = note,
            organization=org,
            user=session_user,
        )
        q_item.save()
        return CreateSalonQueue(ok=True, queue=q_item)


class DeleteSalonQueue(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean()

    def mutate(self, info, id):
        try:
            item = Queue.objects.get(pk=id)
        except Queue.DoesNotExist:
            raise Exception("Queue does not exist")

        item.is_deleted = True
        item.save()
        return DeleteSalonQueue(ok=True)


class UpdateSalonQueue(graphene.Mutation):
    class Arguments:
        id = graphene.Int()
        queue_date_time = graphene.String()
        note = graphene.String()

    ok = graphene.Boolean()
    queue = graphene.Field(QueueType)

    def mutate(self, info, id, **kwargs):
        try:
            item = Queue.objects.get(pk=id)
        except Queue.DoesNotExist:
            raise Exception("Queue does not exist")

        queue_date_time = kwargs.get("queue_date_time")
        note = kwargs.get("note")
        print(queue_date_time)

        item.note = note
        item.queue_date_time = queue_date_time
        item.save()
        return UpdateSalonQueue(ok=True, queue=item)


class Mutation(graphene.ObjectType):
    salon_queue_create = CreateSalonQueue.Field()
    salon_queue_update = UpdateSalonQueue.Field()
    salon_queue_delete = DeleteSalonQueue.Field()


schema_salon_queue = graphene.Schema(query=Query, mutation=Mutation)
