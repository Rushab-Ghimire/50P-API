import graphene
from django.db.models import Q
from graphene_django.types import DjangoObjectType
from ad.models import ReferralCode
from django.core.exceptions import ValidationError
from graphql_jwt.decorators import login_required


class ReferralCodeType(DjangoObjectType):
    class Meta:
        model = ReferralCode
        fields = ["id", "code", "user"]


class ReferralCodeDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(ReferralCodeType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    referral_code_by_user = graphene.Field(ReferralCodeType)

    def resolve_referral_code_by_user(self, info):
        try:
            session_user = info.context.user
            return ReferralCode.objects.get(user=session_user)
        except ReferralCode.DoesNotExist:
            return None


class CreateReferralCode(graphene.Mutation):
    class Arguments:
        pass

    referral_code = graphene.Field(ReferralCodeType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        referral_code = ReferralCode.objects.filter(user=session_user).first()
        if referral_code == None:
            ref_code = session_user.first_name.upper() + str(session_user.id)
            referral_code = ReferralCode.objects.create(
                code=ref_code, 
                user=session_user,
            )        
        return CreateReferralCode(referral_code=referral_code)


class Mutation(graphene.ObjectType):
    referral_code_create = CreateReferralCode.Field()


referral_schema = graphene.Schema(query=Query, mutation=Mutation)
