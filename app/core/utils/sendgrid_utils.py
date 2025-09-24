# SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings


class SendGridUtils:
    def send(from_email, to_emails, subject, content):
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        message = Mail(from_email, to_emails, subject, content)
        sg.send(message)

    def registered_email_verification(to_email, verification_url, business_id = None):
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        if business_id == None:
            from_email = "noreply@tileflexai.com"
            from_name = settings.SYSTEM_NAME
            template_id = "d-22714889f17a4b27b267f6935ddcffed"
        elif business_id == 1:
            from_email = "noreply@daysiai.com"
            from_name = "AskDaysi"
            template_id = "d-8e866642d27d428aabb55de19b4a473f"

        data = {
            "personalizations": [
                {
                    "to": [{"email": to_email}],
                    "dynamic_template_data": {
                        "varification_url": verification_url,
                    },
                },
            ],
            "from": {"email": from_email, "name": from_name},
            "template_id": template_id,
        }

        sg.send(data)

    def password_reset_email(to_email, to_name, reset_url, business_id = None):
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        if business_id == None:
            from_email = "noreply@tileflexai.com"
            from_name = settings.SYSTEM_NAME
            template_id = "d-a978535fd15a4f9e8944db5c5c43c806"
        elif business_id == 1:
            from_email = "noreply@daysiai.com"
            from_name = "AskDaysi"
            template_id = "d-c76fba51da8c47c4b8f5294a59fc60b8"   

        data = {
            "personalizations": [
                {
                    "to": [{"email": to_email, "name": to_name}],
                    "dynamic_template_data": {"reset_url": reset_url, "name": to_name},
                },
            ],
            "from": {"email": from_email, "name": from_name},
            "template_id": template_id,
        }

        sg.send(data)

    def invitation_email(to_email, to_name, name, organization, invtation_url):
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        from_email = "noreply@tileflexai.com"
        from_name = settings.SYSTEM_NAME

        template_id = "d-9447a0668cb747abb9ac41e9fe17e8dd"

        data = {
            "personalizations": [
                {
                    "to": [{"email": to_email, "name": to_name}],
                    "dynamic_template_data": {
                        "invitation_link": invtation_url,
                        "organization": organization,
                        "name": name,
                    },
                },
            ],
            "from": {"email": from_email, "name": from_name},
            "template_id": template_id,
        }

        sg.send(data)

    def html_email(to_email, to_name, html, subject):
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)

        from_email = "noreply@daysiai.com"
        from_name = "AskDaysi"

        template_id = "d-e7a04a2c32304102a408e83ee3b0ffcf"

        data = {
            "personalizations": [
                {
                    "subject": subject,
                    "to": [{"email": to_email, "name": to_name}],
                    "dynamic_template_data": {
                        "html": html,
                        "subject": subject,
                    },
                },
            ],
            "from": {"email": from_email, "name": from_name},
            "template_id": template_id,
        }

        sg.send(data)
