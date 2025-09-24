import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import ChatHistoryCategory
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required


class ChatHistoryCategoryType(DjangoObjectType):
    class Meta:
        model = ChatHistoryCategory
        fields = ["id", "title", "organization", "user"]


class ChatHistoryCategoryDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(ChatHistoryCategoryType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    chat_history_category = graphene.Field(
        ChatHistoryCategoryDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    chat_history_category_by_id = graphene.Field(
        ChatHistoryCategoryType, id=graphene.Int()
    )

    @login_required
    def resolve_chat_history_category(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q(user=info.context.user)
        if search:
            filter = Q(title__icontains=search)

        qs = ChatHistoryCategory.objects.filter(filter)
        qs = qs.order_by("-created_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return ChatHistoryCategoryDataModelType(totalCount=totalCount, rows=qs)

    @login_required
    def resolve_chat_history_category_by_id(self, info, id):
        return ChatHistoryCategory.objects.get(pk=id, user=info.context.user)


class CreateChatHistoryCategory(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)

    chat_history_category = graphene.Field(ChatHistoryCategoryType)

    @login_required
    def mutate(self, info, title):
        session_user = info.context.user

        chat_history_category = ChatHistoryCategory.objects.create(
            title=title, organization=session_user.get_organization(), user=session_user
        )
        return CreateChatHistoryCategory(chat_history_category=chat_history_category)


class UpdateChatHistoryCategory(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()

    ChatHistoryCategory = graphene.Field(ChatHistoryCategoryType)

    @login_required
    def mutate(self, info, id, **kwargs):
        try:
            item = ChatHistoryCategory.objects.get(pk=id, user=info.context.user)
        except ChatHistoryCategory.DoesNotExist:
            raise ValidationError("Category does not exist")

        item.title = kwargs.get("title", item.title)
        item.save(
            update_fields=[
                "title",
            ]
        )
        return UpdateChatHistoryCategory(ChatHistoryCategory=item)


class DeleteChatHistoryCategory(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    @login_required
    def mutate(self, info, id):
        item = ChatHistoryCategory.objects.get(pk=id, user=info.context.user)
        item.is_deleted = True
        item.chat_histories.update(is_deleted=True)
        item.save(update_fields=["is_deleted"])
        return DeleteChatHistoryCategory(ok=True)


class Mutation(graphene.ObjectType):
    chat_history_category_add = CreateChatHistoryCategory.Field()
    chat_history_category_update = UpdateChatHistoryCategory.Field()
    chat_history_category_delete = DeleteChatHistoryCategory.Field()


chat_history_category_schema = graphene.Schema(query=Query, mutation=Mutation)
