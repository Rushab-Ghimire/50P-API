import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import ChatHistory, ChatHistoryCategory
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required


class ChatHistoryType(DjangoObjectType):
    class Meta:
        model = ChatHistory
        fields = ["id", "content", "source", "chat_history_category"]


class ChatHistoryDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(ChatHistoryType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    chat_history = graphene.Field(
        ChatHistoryDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    chat_history_by_category = graphene.List(
        ChatHistoryType, category_id=graphene.Int()
    )

    @login_required
    def resolve_chat_history(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q(user=info.context.user)
        if search:
            filter = Q(source__icontains=search)

        qs = ChatHistory.objects.filter(filter)
        qs = qs.order_by("-created_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return ChatHistoryDataModelType(totalCount=totalCount, rows=qs)

    @login_required
    def resolve_chat_history_by_category(self, info, category_id):
        return ChatHistory.objects.filter(
            chat_history_category_id=category_id, user=info.context.user
        )


class CreateChatHistory(graphene.Mutation):
    class Arguments:
        chat_history_category_id = graphene.Int(required=True)
        source = graphene.String(required=True)
        content = graphene.String(required=True)

    chat_history = graphene.Field(ChatHistoryType)

    @login_required
    def mutate(self, info, chat_history_category_id, source, content):
        if source not in ["bot", "user"]:
            raise ValidationError("Invalid source")

        session_user = info.context.user

        if chat_history_category_id == -1:
            chat_history_category = ChatHistoryCategory.objects.create(
                title="--", organization=session_user.get_organization(), user=session_user
            )
            chat_history_category_id = chat_history_category.id

        try:
            chat_history_category = ChatHistoryCategory.objects.get(
                pk=chat_history_category_id
            )
        except ChatHistoryCategory.DoesNotExist:
            raise ValidationError("Invalid category")

        

        chat_history = ChatHistory.objects.create(
            chat_history_category=chat_history_category,
            source=source,
            content=content,
            user=session_user,
            organization=session_user.get_organization(),
        )
        return CreateChatHistory(chat_history=chat_history)


class Mutation(graphene.ObjectType):
    add_history_item = CreateChatHistory.Field()


chat_history_schema = graphene.Schema(query=Query, mutation=Mutation)
