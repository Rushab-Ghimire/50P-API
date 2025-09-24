import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from graphql import GraphQLError
from agent.models import Ehr
from datetime import datetime
from graphql_jwt.decorators import login_required
from organization.models import Organization
from pubsub.consumer import PubSubBroadcaster

class AgentEhrType(DjangoObjectType):
    class Meta:
        model = Ehr
        fields = "__all__"


class AgentEhrDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(AgentEhrType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    agent_ehr = graphene.Field(
        AgentEhrDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    agent_ehr_by_id = graphene.Field(AgentEhrType, id=graphene.Int())
    agent_ehr_by_phone = graphene.Field(AgentEhrType, phone=graphene.String())

    def resolve_agent_ehr(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        qs = None
        if search:
            filter = (Q(full_name__icontains=search) | Q(phone_number__icontains=search))

        #org = info.context.user.get_organization()

        #qs = Ehr.objects.filter()
        qs = Ehr.objects.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return AgentEhrDataModelType(totalCount=totalCount, rows=qs)

    def resolve_agent_ehr_by_id(root, info, id):
        return Ehr.objects.get(pk=id)

    def resolve_agent_ehr_by_phone(root, info, phone):
        if phone:
            return Ehr.objects.filter(phone_number=phone).first()
        return None


class CreateAgentEhr(graphene.Mutation):
    class Arguments:
        full_name = graphene.String(required=True)
        phone = graphene.String(required=True)
        booking_date_time = graphene.String()
        json = graphene.String()
        org_id = graphene.Int()

    ok = graphene.Boolean()
    agent_ehr = graphene.Field(AgentEhrType)

    def mutate(self, info, **kwargs):
        #print("full name", kwargs.get("full_name"))
        org_id = kwargs.get("org_id")
        org = None
        try:
            org = Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            raise Exception("Organization does not exists")

        item = Ehr()
        item.full_name = kwargs.get("full_name", "")
        item.phone_number = kwargs.get("phone", "")

        booking_date_time = kwargs.get("booking_date_time")
        datetime.strptime(booking_date_time, "%Y-%m-%d %H:%M%z")

        item.booking_date_time = datetime.strptime(booking_date_time, "%Y-%m-%d %H:%M%z")
        item.json = kwargs.get("json")
        item.organization = org
        item.save()

        PubSubBroadcaster.broadcast("common",
            {
                "event_name": "NEW_NOTIFICATION",
                "payload": {
                "id" : item.id,
                "event_type" : "EHR",
                "userTitle": f"TileFlexAI - eHR",
                "message" : f"New eHR Record received"
                }
            }
        )

        return CreateAgentEhr(ok=True, agent_ehr=item)


class Mutation(graphene.ObjectType):
    agent_ehr_create = CreateAgentEhr.Field()


schema_ehr = graphene.Schema(query=Query, mutation=Mutation)
