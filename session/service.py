from typing import List

from django.db import IntegrityError

from cabinet.models import PsychologistSurvey
from session.models import TimeSlot


def create_time_slot(user, slots: List[dict]):

    psychologist = PsychologistSurvey.objects.get(user=user)
    time_slots = [
        TimeSlot(psychologist=psychologist, **slot_data)
        for slot_data in slots
    ]
    try:
        return TimeSlot.objects.bulk_create(time_slots)
    except IntegrityError:
        return {'error': 'this time slot already exists'}