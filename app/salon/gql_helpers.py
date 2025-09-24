from organization.models import Organization


def get_gql_organization(user, organization_id=None):
    """
    Helper function to retrive organization
    This is used on the GraphQL schemas
    user: Authenticated user / Anonymous user of context (info.context.user)
    organization_id: if provided, returns organization with id else will return the context user organization
    """
    if organization_id:
        try:
            return Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise Exception("Organization does not exit")
    else:
        if not user.is_anonymous:
            return user.get_organization()



def gql_authentication_required(info):
    user = info.context.user
    if user.is_anonymous:
        raise Exception("Authentication Failure: Your must be signed in")
