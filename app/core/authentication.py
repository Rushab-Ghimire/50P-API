from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from graphql_jwt.utils import jwt_decode, get_payload
from django.contrib.auth import get_user_model
from drf_spectacular.extensions import OpenApiAuthenticationExtension

User = get_user_model()


class GraphQLJWTAuthentication(BaseAuthentication):
    """Authenticate Bearer token using graphql_jwt"""

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split(" ")[1]
        try:
            payload = jwt_decode(token)
            user = User.objects.get(email=payload.get("email"))
            return (user, token)
        except Exception as e:
            raise AuthenticationFailed(f"Invalid token: {str(e)}")


class GraphQLJWTAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = (
        "core.authentication.GraphQLJWTAuthentication"  # Full path to your class
    )
    name = "GraphQLJWTAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "http",
            "scheme": "bearer",  # Or the scheme your custom auth uses
            "bearerFormat": "JWT",
        }
