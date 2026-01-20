import graphene
from core.utils.send_sms_utils import send_sms_gateway

class SendManualSMS(graphene.Mutation):
    class Arguments:
        phone_number = graphene.String(required=True)
        message = graphene.String(required=True)

    success = graphene.Boolean()
    feedback = graphene.String()

    def mutate(self, info, phone_number, message):
        result = send_sms_gateway(phone_number, message)

        if result:
            return SendManualSMS(success = True, feedback="SMS sent successfully")
        
        else:
            return SendManualSMS(success = False, feedback="Failed tt send SMS.")
        

class Mutation(graphene.ObjectType):
    send_sms = SendManualSMS.Field()

sms_schema = graphene.Schema(mutation = Mutation)