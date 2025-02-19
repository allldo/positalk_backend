from datetime import datetime, timedelta
from typing import List

from django.db import IntegrityError
from django.db.models import Q, Exists

from cabinet.models import PsychologistSurvey
from session.models import TimeSlot, Session


def is_time_slot_available(psychologist, start_time, end_time, user) -> [bool, str]:
    start_time = datetime.strptime(start_time.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")
    end_time = datetime.strptime(end_time.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")
    start_date = start_time.date()
    day_of_week = start_date.weekday()

    if start_time < datetime.now():
        return [False, "Нельзя записываться на прошедшую дату"]

    existing_sessions = Session.objects.filter(
        client=user,
        psychologist=psychologist,
        start_time__lt=end_time,
        end_time__gt=start_time,
        status__in=['awaiting_payment', 'awaiting']
    ).exists()

    if existing_sessions:
        return [False, "У вас уже есть сессия в данный день"]

    overlapping_sessions = Session.objects.filter(
        psychologist=psychologist,
        start_time__date=start_date,
    ).exclude(status__in=['awaiting_payment', 'cancelled', 'complete']).filter(
        Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
    )

    time_slots = TimeSlot.objects.filter(
        psychologist=psychologist,
        day_of_week=day_of_week,
        is_available=True
    ).exclude(
        Exists(overlapping_sessions)
    )

    for time_slot in time_slots:
        slot_start = datetime.combine(start_date, time_slot.time)
        slot_end = slot_start + timedelta(hours=psychologist.session_duration)
        if slot_start <= start_time < slot_end and end_time == slot_end:
            return [True, ""]

    return [False, "Не получится провести сессию в это время"]


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


