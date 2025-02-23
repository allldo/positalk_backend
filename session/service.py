from datetime import datetime, timedelta
from typing import List

import pytz
from django.db import IntegrityError
from django.db.models import Q, Exists

from cabinet.models import PsychologistSurvey, Survey
from session.models import TimeSlot, Session


def is_time_slot_available(psychologist, start_time, end_time, user) -> [bool, str]:
    survey = Survey.objects.filter(user=user).first()
    if not survey or not survey.timezone:
        return [False, "Не удалось определить ваш часовой пояс"]

    client_tz = pytz.timezone(survey.timezone)
    psychologist_tz = pytz.timezone(psychologist.timezone)

    # print(client_tz.localize(datetime.strptime(start_time.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")))
    start_time = client_tz.localize(datetime.strptime(start_time.rstrip("Z"), "%Y-%m-%dT%H:%M:%S"))
    end_time = client_tz.localize(datetime.strptime(end_time.rstrip("Z"), "%Y-%m-%dT%H:%M:%S"))
    # print(start_time, "start time", end_time, "end time")
    start_date = start_time.date()
    day_of_week = start_date.weekday()

    if start_time < datetime.now(client_tz):
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
    start_time_psychologist = start_time.astimezone(psychologist_tz)
    end_time_psychologist = end_time.astimezone(psychologist_tz)
    start_date_psychologist = start_time_psychologist.date()
    day_of_week = start_date_psychologist.weekday()
    overlapping_sessions = Session.objects.filter(
        psychologist=psychologist,
        start_time__date=start_date,
    ).exclude(status__in=['awaiting_payment', 'cancelled', 'complete']).filter(
        Q(start_time__lt=end_time_psychologist) & Q(end_time__gt=start_time_psychologist)
    )

    time_slots = TimeSlot.objects.filter(
        psychologist=psychologist,
        day_of_week=day_of_week,
        is_available=True
    ).exclude(
        Exists(overlapping_sessions)
    )
    for time_slot in time_slots:
        slot_start = psychologist_tz.localize(datetime.combine(start_date, time_slot.time))
        slot_end = slot_start + timedelta(hours=psychologist.session_duration)

        print(slot_start, "slot start time", slot_end, "slot end time", start_time, "start time", end_time, "end time")
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


