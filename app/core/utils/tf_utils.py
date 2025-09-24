"""
Utilites functions
"""

import uuid
from django.conf import settings
from django.apps import apps
from django.templatetags.static import static
from django.db import transaction
from salon.models.user_file import UserFileTypes
from twilio.rest import Client
import secrets
from openai import OpenAI
import json
from core.utils.email_utils import EmailUtils
from subscription.helpers import SubscriptionHelper


def referralEmailChain(referral):
    #print("referral", referral)
    referee = referral.referred_user
    referrer = referral.user
    referral_code = referral.referral_code
    #print(f'From {referrer} to {referee} with {referral_code}')

    html = f'Welcome to AskDaysi & Congratulations.<br/>You have used a Referral Code - {referral_code} for Sign-up.<br/><br/>Congratulations !, You have received a Premium Membership for 1 Month.'
    #print("to Referee - ", referee.email, html, "Welcome to AskDaysi & Congratulations")
    try:
        SubscriptionHelper.assing_referee_subscription_for_new_user(referee)
    except Exception as e:
        print(f"Failed to assign Premium referee plan to user {referee.id}")
        print(e)

    EmailUtils.html_email(
        to_email = referee.email,
        to_name = "AskDaysi",
        html = html,
        subject = "Welcome to AskDaysi & Congratulations"
    )

    html = f'Your Referral Code - {referral_code} has been used for Registration in AskDaysi'
    #print("to referrer - ", referrer.email, html, "Referral Code Used for Registration")
    EmailUtils.html_email(
        to_email = referrer.email,
        to_name = "AskDaysi",
        html = html,
        subject = "Referral Code Used for Registration"
    )

    print("count = ", referral_code.referral_set.count())

    if referral_code.referral_set.count() == 3:
        html = f'Congratulations !<br/>Your referral has been used by 3 new Users.<br/>You have received a Premium Membership for 3 months.'
        #print("to referrer - ", referrer.email, html, "Congratulations for 3 Months Membership Upgrade")
        try:
            SubscriptionHelper.assign_referrer_subscription(referrer)
        except Exception as e:
            print(f"Failed to assign Premium referrer plan to user {referrer.id}")
            print(e)

        EmailUtils.html_email(
            to_email = referrer.email,
            to_name = "AskDaysi",
            html = html,
            subject = "Congratulations for 3 Months Membership Upgrade"
        )


    if referral_code.referral_set.count() == 2:
        html = f'Your referral has been used by 2 new Users.<br/>You are almost there to receive a Premium Membership for 3 months as soon and one more user signs up.'
        #print("to referrer - ", referrer.email, html, "Almost there for 3 Months Membership Upgrade")
        EmailUtils.html_email(
            to_email = referrer.email,
            to_name = "AskDaysi",
            html = html,
            subject = "Almost there for 3 Months Membership Upgrade"
        )

    #Write all account upgrade codes after email above
    pass


def get_unique_key():
    return str(uuid.uuid4())


def generate_salon_order_code():
    Order = apps.get_model("salon", "Order")
    with transaction.atomic():
        last_order = (
            Order.objects.select_for_update().order_by("-id").first()
        )  # Fetch the most recent order
        if last_order and last_order.order_code:
            last_code = last_order.order_code
            order_num = int(last_code.split("-")[1]) + 1
        else:
            order_num = 1

        order_code = f"ORD-{order_num:05d}"

        while Order.objects.filter(order_code=order_code).exists():
            order_num += 1
            order_code = f"ORD-{order_num:05d}"

    return order_code


def generate_salon_receipt_number():
    Order = apps.get_model("salon", "Order")
    with transaction.atomic():
        last_order = (
            Order.objects.select_for_update().order_by("-id").first()
        )  # Fetch the most recent order
        if last_order and last_order.receipt_number:
            last_receipt = last_order.receipt_number
            receipt_num = int(last_receipt.split("-")[1]) + 1
        else:
            receipt_num = 1

        receipt_number = f"REC-{receipt_num:05d}"

        while Order.objects.filter(receipt_number=receipt_number).exists():
            receipt_num += 1
            receipt_number = f"REC-{receipt_num:05d}"

    return receipt_number


def get_password_reset_request_url(code, b_id):
    """Get the password reset request url for the given code"""
    if b_id == 1:
        return f"https://app.askdaysi.com/reset-password?token={code}"
    else:
        return f"{settings.SYSTEM_APP_URL}/reset-password?token={code}"


def get_amount_with_currency_code(amount):
    """Return amount with currency code"""
    return f"USD {amount}"


def get_user_file_URL(user_id, key, type):
    return _get_file_URL(owner_id=user_id, owner_type="user", key=key, type=type)


def get_customer_file_URL(customer_id, key, type):
    return _get_file_URL(
        owner_id=customer_id, owner_type="customer", key=key, type=type
    )


def get_file_URL_by_unique_id(unique_id, type):
    modelObject = None
    not_found_icon = static("document-placeholder.png")
    if type.lower() == UserFileTypes.MEDIA:
        modelObject = apps.get_model("salon", "Media")
        query = "SELECT m.id, m.file_path FROM salon_media as m"
        not_found_icon = static("image-placeholder.png")
    if type.lower() == UserFileTypes.DOCUMENT:
        modelObject = apps.get_model("salon", "Document")
        query = "SELECT m.id, m.file_path FROM salon_document as m"

    query = f"{query} WHERE unique_id = '{unique_id}'"

    not_found_file = f"{settings.BASE_URL}{not_found_icon}"
    if not modelObject:
        return not_found_file

    file = modelObject.objects.raw(
        query,
        [unique_id],
    )
    if file and file[0] and file[0].file_path:
        return f"{settings.BASE_URL}{file[0].file_path.url}"

    return not_found_file


def _get_file_URL(
    owner_id,
    owner_type,
    key,
    type,
):
    modelObject = None
    not_found_icon = static("document-placeholder.png")
    if type.lower() == UserFileTypes.MEDIA:
        modelObject = apps.get_model("salon", "Media")
        query = "SELECT m.id, m.file_path FROM salon_media as m"
        not_found_icon = static("image-placeholder.png")
    if type.lower() == UserFileTypes.DOCUMENT:
        modelObject = apps.get_model("salon", "Document")
        query = "SELECT m.id, m.file_path FROM salon_document as m"

    not_found_file = f"{settings.BASE_URL}{not_found_icon}"
    if not modelObject:
        return not_found_file

    query += " JOIN salon_user_file as suf ON m.unique_id = suf.unique_id"

    if owner_type == "user":
        query += " WHERE suf.linked_user_id=%s and suf.key=%s"
    elif owner_type == "customer":
        query += " WHERE suf.customer_id=%s and suf.key=%s"
    else:
        return not_found_file

    file = modelObject.objects.raw(
        query,
        [owner_id, key],
    )
    if file and file[0] and file[0].file_path:
        return f"{settings.BASE_URL}{file[0].file_path.url}"

    return not_found_file


def _ad_get_file_URL(**kwargs):
    """
    To get ad model file urls
    kwargs: owner_id, key, type, unique_id
    """
    modelObject = None
    type = kwargs.get("type")
    not_found_icon = static("document-placeholder.png")
    if type.lower() == UserFileTypes.MEDIA:
        modelObject = apps.get_model("ad", "ADMedia")
        query = "SELECT m.id, m.file_path FROM ad_media as m"
        not_found_icon = static("image-placeholder.png")
    if type.lower() == UserFileTypes.DOCUMENT:
        modelObject = apps.get_model("ad", "ADDocument")
        query = "SELECT m.id, m.file_path FROM ad_document as m"

    not_found_file = f"{settings.BASE_URL}{not_found_icon}"
    if not modelObject:
        return not_found_file

    unique_id = kwargs.get("unique_id")
    if unique_id:
        query += " WHERE m.unique_id = %s"
        file = modelObject.objects.raw(
            query,
            [unique_id],
        )

    else:
        owner_id = kwargs.get("owner_id")
        key = kwargs.get("key")

        if owner_id is None or key is None:
            return not_found_file

        query += (
            " JOIN ad_user_file as uf ON m.unique_id = uf.unique_id"
            " WHERE uf.linked_user_id=%s and uf.key=%s"
        )
        file = modelObject.objects.raw(
            query,
            [owner_id, key],
        )

    if file and file[0] and file[0].file_path:
        return f"{settings.BASE_URL}{file[0].file_path.url}"

    return not_found_file


def get_ad_user_file_URL(user_id, key, type):
    return _ad_get_file_URL(owner_id=user_id, key=key, type=type)

def get_ad_file_URL_by_unique_id(unique_id, type):
    return _ad_get_file_URL(unique_id=unique_id, type=type)

def get_default_media_url():
    return f"{settings.BASE_URL}{static('image-placeholder.png')}"

def convert_string_to_float(value):
    """
    Converts the given value to float.
    Returns 0 if not able to convert
    """
    try:
        return float(value)
    except ValueError:
        return 0


def get_otp(length=6):
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def send_sms(to_number, body_text):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN

    client = Client(account_sid, auth_token)

    client.messages.create(
        to=to_number, from_=settings.TWILIO_OTP_FROM_NUMBER, body=body_text
    )

def translate_text(text, target_language):
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a multilanguage translator. You can detect the language of the text and response on the requested language",
            },
            {
                "role": "user",
                "content": f"Translate to {target_language}: {text}",
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "language_detection",
                "schema": {
                    "type": "object",
                    "properties": {
                        "translated_text": {
                            "type": "string",
                            "description": "The text translated to the requested language.",
                        },
                    },
                    "required": [
                        "translated_text",
                    ],
                    "additionalProperties": False,
                },
                "strict": True
            },
        },
    )

    result = json.loads(response.choices[0].message.content)
    return result.get("translated_text")
