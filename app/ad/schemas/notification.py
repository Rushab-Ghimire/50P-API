import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import Notification
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required
from django.contrib.auth import get_user_model

class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = "__all__"


class NotificationDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(NotificationType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    notification = graphene.Field(
        NotificationDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )

    notification_by_id = graphene.Field(NotificationType, id=graphene.Int())

    @login_required
    def resolve_notification(self, info, **kwargs):
        session_user = info.context.user

        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q(to_user=session_user)
        if search:
            filter &= Q(content__icontains=search)

        qs = Notification.objects.filter(filter)
        qs = qs.order_by("-created_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return NotificationDataModelType(totalCount=totalCount, rows=qs)

    @login_required
    def resolve_notification_by_id(self, info, id):

        #NotificationUtils.notify(title = "New Notification", message="Nice work", toUser = 91, context=info.context)

        return Notification.objects.get(pk=id, to_user=info.context.user)


class CreateNotification(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)
        to_user = graphene.Int(required=True)
        data_string = graphene.String()

    notification = graphene.Field(NotificationType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        try:
            to_user = get_user_model().objects.get(
                pk=kwargs.get("to_user")
            )
        except get_user_model().DoesNotExist:
            raise ValidationError("Destination User does not exist")

        notification = Notification.objects.create(
            content=kwargs.get("content"),
            data_x=kwargs.get("data_string", ""),
            to_user=to_user,
            organization=org,
            user=session_user,
        )
        return CreateNotification(notification=notification)


class UpdateNotification(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        content = graphene.String()
        is_checked = graphene.Boolean()

    Notification = graphene.Field(NotificationType)

    @login_required
    def mutate(self, info, id, **kwargs):
        try:
            item = Notification.objects.get(pk=id)
        except Notification.DoesNotExist:
            raise ValidationError("Notification does not exist")

        item.content = kwargs.get("content", item.content)
        item.is_checked = kwargs.get("is_checked", item.is_checked)
        item.save(update_fields=["content", "is_checked"])

        return UpdateNotification(Notification=item)


class DeleteNotification(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    @login_required
    def mutate(self, info, id):
        try:
            item = Notification.objects.get(pk=id)
        except Notification.DoesNotExist:
            raise ValidationError("Notification does not exist")

        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteNotification(ok=True)


class Mutation(graphene.ObjectType):
    notification_add = CreateNotification.Field()
    notification_update = UpdateNotification.Field()
    notification_delete = DeleteNotification.Field()


notification_schema = graphene.Schema(query=Query, mutation=Mutation)
