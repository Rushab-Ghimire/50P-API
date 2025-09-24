import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import Language
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required


class LanguageType(DjangoObjectType):
    class Meta:
        model = Language
        fields = ["id", "title"]


class LanguageDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(LanguageType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    language = graphene.Field(
        LanguageDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    language_by_id = graphene.Field(LanguageType, id=graphene.Int())

    def resolve_language(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")

        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        qs = Language.objects.filter(filter)
        qs = qs.order_by("-title")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return LanguageDataModelType(totalCount=totalCount, rows=qs)

    def resolve_language_by_id(self, info, id):
        return Language.objects.get(pk=id)


class CreateLanguage(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)

    language = graphene.Field(LanguageType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user

        language = Language.objects.create(
            title=kwargs.get("title"),
            organization=session_user.get_organization(),
            user=session_user,
        )
        return CreateLanguage(language=language)


class UpdateLanguage(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()

    Language = graphene.Field(LanguageType)

    @login_required
    def mutate(self, info, id, **kwargs):
        try:
            item = Language.objects.get(pk=id)
        except Language.DoesNotExist:
            raise ValidationError("Language does not exist")

        item.title = kwargs.get("title", item.title)

        item.save(
            update_fields=[
                "title",
            ]
        )
        return UpdateLanguage(Language=item)


class DeleteLanguage(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Int()

    @login_required
    def mutate(self, info, id):
        item = Language.objects.get(pk=id, user=info.context.user)
        item.is_deleted = True
        item.save(update_fields=["is_deleted"])
        return DeleteLanguage(ok=True)


class Mutation(graphene.ObjectType):
    language_add = CreateLanguage.Field()
    language_update = UpdateLanguage.Field()
    language_delete = DeleteLanguage.Field()


language_schema = graphene.Schema(query=Query, mutation=Mutation)
