import json

import requests
from django.conf import settings

def send_sms(phone_number, code):
    headers = {
        "Authorization": f"Bearer {settings.SMS_KEY}"
    }
    data = json.dumps({"number":f"{settings.API_PHONE_NUMBER}", "destination": phone_number, "text": code})
    response = requests.post("https://api.exolve.ru/messaging/v1/SendSMS", data=data,headers=headers)
    print(response.json())