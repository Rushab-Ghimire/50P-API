import requests
from django.conf import settings
from datetime import datetime

def send_sms_gateway(phone_number: str, message_text: str) -> bool:
    print(f"DEBUG: INFOBIP_ENABLED is currently: {getattr(settings, 'INFOBIP_ENABLED', 'NOT FOUND')}")

    phone_number = phone_number.lstrip('+').strip()

    if phone_number.startswith('977'):
        formatted_number = f"+{phone_number}"
    
    else:
        formatted_number = f"+977{phone_number}"
        
    if not getattr(settings, "INFOBIP_ENABLED", False):
        print(f"SMS TEST :")
        print(f"TIME: {datetime.now()}")
        print(f"TO: {formatted_number}")
        print(f"TEXT: {message_text}")
        print(f"--------------------------\n")
        return True
    
    print(f"DEBUG KEY: {settings.INFOBIP_API_KEY}")
    print(f"DEBUG URL: {settings.INFOBIP_BASE_URL}")
    print(f"DEBUG SENDER: {settings.INFOBIP_SENDER_ID}")

    if not all([settings.INFOBIP_BASE_URL, settings.INFOBIP_API_KEY, settings.INFOBIP_SENDER_ID]):
        print("ERROR: INFOBIP credentials missing.")
        return False
    
    api_url = f"https://{settings.INFOBIP_BASE_URL}/sms/2/text/advanced"

    headers = {
        'Authorization': f'App {settings.INFOBIP_API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    payload = {
        "messages": [{
            "destinations": [{"to": formatted_number}],
            "from": settings.INFOBIP_SENDER_ID,
            "text": message_text
        }]
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        print(f"INFOBIP RESPONSE JSON: {response.json()}") 

        if response.status_code == 200:
            print(f"SUCCESS: SMS sent to {formatted_number}")
            return True
        
        else:
            print(f"FAILED: Status {response.status_code}, Body: {response.text}")
            return False
    
    except Exception as e:
        print(f"Network Error:{str(e)}")
        return False