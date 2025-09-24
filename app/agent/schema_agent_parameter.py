import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q
from graphql import GraphQLError
from agent.models import Parameter, AgentType

from graphql_jwt.decorators import login_required


AgentTypeEnum = graphene.Enum.from_enum(AgentType)
class AgentParameterType(DjangoObjectType):
    class Meta:
        model = Parameter
        fields = "__all__"
    agent_type = graphene.Field(AgentTypeEnum)

    def resolve_agent_type(self, info):
        return self.agent_type


class AgentParameterDataModelType(graphene.ObjectType):
    totalCount = graphene.Int()
    rows = graphene.List(AgentParameterType)

    class Meta:
        fields = ("totalCount", "rows")


class Query(graphene.ObjectType):
    agent_parameter = graphene.Field(
        AgentParameterDataModelType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    agent_parameter_by_id = graphene.Field(AgentParameterType, id=graphene.Int())

    @login_required
    def resolve_agent_parameter(self, info, **kwargs):
        search = kwargs.get("search")
        skip = kwargs.get("skip")
        first = kwargs.get("first")
        filter = Q()
        if search:
            filter = Q(title__icontains=search)

        org = info.context.user.get_organization()

        qs = Parameter.objects.filter(organization=org)
        qs = qs.filter(filter)
        qs = qs.order_by("-modified_date")
        totalCount = qs.count()

        if skip:
            qs = qs[skip:]
        if first:
            qs = qs[:first]

        return AgentParameterDataModelType(totalCount=totalCount, rows=qs)

    @login_required
    def resolve_agent_parameter_by_id(root, info, id):
        org = info.context.user.get_organization()
        return Parameter.objects.get(pk=id, organization=org)


class CreateAgentParameter(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        agent_type = graphene.String()
        system_message = graphene.String()
        call_connection_message = graphene.String()
        call_initial_message = graphene.String()

    ok = graphene.Boolean()
    agent_parameter = graphene.Field(AgentParameterType)

    @login_required
    def mutate(self, info, **kwargs):
        session_user = info.context.user
        org = session_user.get_organization()

        item = Parameter()
        item.title = kwargs.get("title")
        item.description = kwargs.get("description")
        agent_type = kwargs.get("agent_type")
        if agent_type and agent_type.lower() in AgentType.values:
            item.agent_type = agent_type.lower()

        system_message = kwargs.get("system_message")
        if system_message:
            item.system_message = system_message

        item.call_connection_message = kwargs.get("call_connection_message")
        item.call_initial_message = kwargs.get("call_initial_message")

        item.organization = org
        item.user = session_user

        item.save()
        return CreateAgentParameter(ok=True, agent_parameter=item)


class DeleteAgentParameter(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(self, info, id):
        org = info.context.user.get_organization()
        try:
            item = Parameter.objects.get(pk=id, organization=org)
        except Parameter.DoesNotExist:
            raise Exception("Floor Plan does not exist")

        item.is_deleted = True
        item.save()
        return DeleteAgentParameter(ok=True)


class UpdateAgentParameter(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        description = graphene.String()
        agent_type = graphene.String()
        system_message = graphene.String()
        call_connection_message = graphene.String()
        call_initial_message = graphene.String()

    ok = graphene.Boolean()
    agent_parameter = graphene.Field(AgentParameterType)

    @login_required
    def mutate(self, info, id, **kwargs):
        org = info.context.user.get_organization()
        try:
            item = Parameter.objects.get(pk=id, organization=org)
        except Parameter.DoesNotExist:
            raise Exception("Agent Parameter does not exist")

        item.title = kwargs.get("title", item.title)
        item.description = kwargs.get("description", item.description)

        agent_type = kwargs.get("agent_type")
        if agent_type and agent_type.lower() in AgentType.values:
                item.agent_type = agent_type.lower()

        item.system_message = kwargs.get("system_message", item.system_message)
        item.call_connection_message = kwargs.get(
            "call_connection_message", item.call_connection_message
        )
        item.call_initial_message = kwargs.get(
            "call_initial_message", item.call_initial_message
        )

        item.save()
        return UpdateAgentParameter(ok=True, agent_parameter=item)


class Mutation(graphene.ObjectType):
    agent_parameter_create = CreateAgentParameter.Field()
    agent_parameter_update = UpdateAgentParameter.Field()
    agent_parameter_delete = DeleteAgentParameter.Field()


schema_agent_parameter = graphene.Schema(query=Query, mutation=Mutation)
