import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import ChatKeyword, ChatHistoryCategory, ChatHistory
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required
from core.utils.interaction_utils import InteractionUtils

class ChatKeywordType(DjangoObjectType):
    class Meta:
        model = ChatKeyword
        fields = ["id", "keywords", "chat_history_category"]


class Query(graphene.ObjectType):
    chat_keyword_by_thread_id = graphene.Field(
        ChatKeywordType, thread_id=graphene.Int()
    )

    @login_required
    def resolve_chat_keyword_by_thread_id(self, info, thread_id):
        if not ChatHistoryCategory.objects.filter(pk=thread_id).exists():
            raise ValidationError("Invalid thread")

        chat_keyword = ChatKeyword.objects.filter(
            chat_history_category_id=thread_id
        ).first()

        if not chat_keyword:
            chat_history_content = ", ".join(
                ChatHistory.objects.filter(chat_history_category=thread_id)
                .values_list("content", flat=True)
                .distinct()
            )

            generated_keywords = InteractionUtils.get_keywords_for_content(chat_history_content)
            chat_keyword = ChatKeyword.objects.create(
                keywords=generated_keywords, chat_history_category_id=thread_id, user=info.context.user
            )

        return chat_keyword


class UpdateChatKeyword(graphene.Mutation):
    class Arguments:
        thread_id = graphene.Int(required=True)
        keywords = graphene.String(required=True)

    chat_keyword = graphene.Field(ChatKeywordType)

    @login_required
    def mutate(self, info, thread_id, keywords):
        if not ChatHistoryCategory.objects.filter(pk=thread_id).exists():
            raise ValidationError("Invalid thread")

        keyword_list = [key.strip() for key in keywords.split("~") if key.strip()]

        chat_keyword, _ = ChatKeyword.objects.update_or_create(
            chat_history_category_id=thread_id,
            defaults={"keywords": keyword_list},
        )

        return UpdateChatKeyword(chat_keyword=chat_keyword)


class Mutation(graphene.ObjectType):
    update_chat_keyword = UpdateChatKeyword.Field()


chat_keyword_schema = graphene.Schema(query=Query, mutation=Mutation)
