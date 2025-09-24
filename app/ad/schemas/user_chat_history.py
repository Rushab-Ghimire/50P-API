import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import UserChatHistory
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required
from django.contrib.auth import get_user_model
from core.utils.notification_utils import NotificationUtils
from core.utils.tf_utils import translate_text


class UserChatHistoryType(DjangoObjectType):
    class Meta:
        model = UserChatHistory
        fields = "__all__"


class UserChatHistoryDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(UserChatHistoryType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    user_chat_history = graphene.Field(
        UserChatHistoryDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
        booking_id=graphene.Int(),
    )

    @login_required
    def resolve_user_chat_history(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        booking_id = kwargs.get("booking_id")

        filter = Q()
        #Q(organization=org) & Q(user=session_user)
        if search:
            filter &= Q(content__icontains=search)

        if booking_id:
            filter &= Q(booking_id=booking_id)

        qs = UserChatHistory.objects.filter(filter)
        qs = qs.order_by("created_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return UserChatHistoryDataModelType(totalCount=totalCount, rows=qs)


class CreateUserChatHistory(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)
        destination_user_id = graphene.Int(required=True)
        destination_user_lang = graphene.String()
        booking_id = graphene.Int(required=True)

    user_chat_history = graphene.Field(UserChatHistoryType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        try:
            destination_user = get_user_model().objects.get(
                pk=kwargs.get("destination_user_id")
            )
        except get_user_model().DoesNotExist:
            raise ValidationError("Destination User does not exist")

        destination_user_lang = kwargs.get("destination_user_lang", "English")
        content_destination = translate_text(kwargs.get("content"), destination_user_lang)

        user_chat_history = UserChatHistory.objects.create(
            content=kwargs.get("content"),
            content_destination=content_destination,
            destination_user=destination_user,
            booking_id=kwargs.get("booking_id"),
            organization=org,
            user=session_user,
        )

        NotificationUtils.message_without_history(kwargs.get("booking_id"), destination_user.id, content_destination)

        return CreateUserChatHistory(user_chat_history=user_chat_history)


class UpdateUserChatHistory(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        content = graphene.String()

    UserChatHistory = graphene.Field(UserChatHistoryType)

    @login_required
    def mutate(self, info, id, **kwargs):
        try:
            item = UserChatHistory.objects.get(pk=id, user=info.context.user)
        except UserChatHistory.DoesNotExist:
            raise ValidationError("Chat history does not exist")

        item.content = kwargs.get("content", item.content)
        item.save(update_fields=["content"])

        return UpdateUserChatHistory(UserChatHistory=item)


class DeleteUserChatHistory(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    @login_required
    def mutate(self, info, id):
        try:
            item = UserChatHistory.objects.get(pk=id, user=info.context.user)
        except UserChatHistory.DoesNotExist:
            raise ValidationError("Chat history does not exist")

        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteUserChatHistory(ok=True)

class NotifyIsTyping(graphene.Mutation):
    class Arguments:
        destination_user_id = graphene.Int(required=True)
        booking_id = graphene.Int(required=True)

    ok = graphene.Int()

    @login_required
    def mutate(self, info, destination_user_id, booking_id):
        NotificationUtils.notify_without_history(booking_id, destination_user_id)

        return NotifyIsTyping(ok=True)


class Mutation(graphene.ObjectType):
    user_chat_history_add = CreateUserChatHistory.Field()
    user_chat_history_update = UpdateUserChatHistory.Field()
    user_chat_history_delete = DeleteUserChatHistory.Field()
    notify_is_typing = NotifyIsTyping.Field()


user_chat_history_schema = graphene.Schema(query=Query, mutation=Mutation)
