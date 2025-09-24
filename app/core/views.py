"""
Core views for app.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .utils.email_utils import EmailUtils
from authtf import schema_user
from subscription.payment_utils import PaymentUtils
from openai import OpenAI


@api_view(["GET"])
def health_check(request):

    login_res = schema_user.schema_user.execute(
        """
        mutation MyMutation {
            tokenAuth(password: "%s", email: "%s") {
                token
            }
        }
        """
        % ("demo@123", "demo@askdaysi.com"),
        context=request,
    )

    try:
        login_check = False if login_res.errors else True
        api_status = "on" if login_check else "off"
    except Exception as e:
        print(e)
        api_status = "off"

    try:
        PaymentUtils().get_customer_list({"limit": 1})
        chargebee_status = "on"
    except Exception as e:
        print(e)
        chargebee_status = "off"

    try:
        OpenAI().chat.completions.create(
            model="o4-mini",
            messages=[{"role": "user", "content": "hello"}],
            max_completion_tokens=10,
        )

        openai_status = "on"

    except Exception as e:
        print(e)
        openai_status = "off"

    try:
        EmailUtils.html_email(
            to_email="test@askdaysi.com",
            to_name="Test",
            html="this is a status test for sendgrid api",
            subject="Status Test",
        )
        sendgrid_status = "on"
    except Exception as e:
        print(e)
        sendgrid_status = "off"

    return Response(
        {
            "api": api_status,
            "chargebee": chargebee_status,
            "openai": openai_status,
            "sendgrid": sendgrid_status,
        }
    )


@api_view(["GET"])
def sendgrid_mail_check(request):
    # EmailUtils.send("noreply@tileflexai.com", "kamal.kafle1@gmail.com", "Welcome to TileFlexAi", "This is a great news, welome to the team. We are really excited to have you here.")
    print(request.user)
    EmailUtils.registered_email_verification(
        {"email": "kamal.kafle1@gmail.com", "name": "Kamal Kafle"}
    )
    return Response({"message": "Mail sent."})
