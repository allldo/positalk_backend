import json

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from session.models import TimeSlot


def send_sms(phone_number, code):
    headers = {
        "Authorization": f"Bearer {settings.SMS_KEY}"
    }
    data = json.dumps({"number":f"{settings.API_PHONE_NUMBER}", "destination": phone_number, "text": code})
    response = requests.post("https://api.exolve.ru/messaging/v1/SendSMS", data=data,headers=headers)
    print(response.json())


def adjust_time_slot(psychologist, time_slot_data):
    time_slot_id = time_slot_data.get("id")

    if time_slot_id:
        try:
            time_slot = TimeSlot.objects.get(id=time_slot_id, psychologist=psychologist)
            time_slot.day_of_week = time_slot_data["day_of_week"]
            time_slot.time = time_slot_data["time"]
            time_slot.is_available = time_slot_data.get("is_available", time_slot.is_available)
            time_slot.save()
            return {"status": f"Time slot {time_slot.id} updated"}
        except ObjectDoesNotExist:
            return {"status": f"Time slot {time_slot_id} not found", "error": True}
    else:
        time_slot, created = TimeSlot.objects.get_or_create(
                psychologist=psychologist,
                day_of_week=time_slot_data["day_of_week"],
                time=time_slot_data["time"],
                defaults={"is_available": time_slot_data.get("is_available", True)}
        )
        if created:
            return {"status": "Time slot created"}
        else:
            return {"status": f"Time slot {time_slot.id} already exists"}
