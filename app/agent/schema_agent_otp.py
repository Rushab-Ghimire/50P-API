import graphene
from agent.models import Otp
from core.utils.tf_utils import get_otp, send_sms
from graphql import GraphQLError
import re

class AgentVerifyOtpType(graphene.ObjectType):
    otp_matched = graphene.Boolean()


class Query(graphene.ObjectType):

    agent_verify_otp = graphene.Field(
        AgentVerifyOtpType,
        phone=graphene.String(required=True),
        otp=graphene.String(required=True),
    )

    def resolve_agent_verify_otp(self, info, phone, otp):
        try:
            phone = phone.replace(" ", "").replace("-", "")
            agent_otp = Otp.objects.get(phone=phone, unique_id=otp)
            agent_otp.delete()
            return AgentVerifyOtpType(otp_matched=True)

        except Otp.DoesNotExist:
            return AgentVerifyOtpType(otp_matched=False)


class CreateOtp(graphene.Mutation):
    ok = graphene.Boolean()
    class Arguments:
        phone = graphene.String(required=True)

    def mutate(self, info, phone):
        phone = phone.replace(" ", "").replace("-", "")
        if not re.match(r'^\+\d{1,3}\d{10}$', phone):
            raise GraphQLError("Invalid phone number format.")

        unique_id = get_otp()
        otp, created = Otp.objects.update_or_create(
            phone=phone, defaults={"unique_id": unique_id}
        )

        try:
            send_sms(
                phone,
                f"Your verification code is: {unique_id}."
                " Please do not share this code with anyone.",
            )
        except Exception as e:
            raise GraphQLError("Failed to send OTP")

        return CreateOtp(ok=True)


class Mutation(graphene.ObjectType):
    agent_create_otp = CreateOtp.Field()


schema_agent_otp = graphene.Schema(query=Query, mutation=Mutation)
