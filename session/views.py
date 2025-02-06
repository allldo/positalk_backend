from datetime import datetime, timedelta, date

from django.db.models import  OuterRef, Subquery, DateTimeField
from django.utils.timezone import now
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from cabinet.models import PsychologistSurvey
from session.models import TimeSlot, Session
from session.serializers import TimeSlotSerializer, PsychologistSessionSerializer
from session.service import create_time_slot


class PsychologistSessionListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PsychologistSessionSerializer

    def get_queryset(self):
        user = self.request.user

        last_session_qs = Session.objects.filter(
            client=user,
            psychologist=OuterRef('pk'),
            start_time__lt=now()
        ).order_by('-start_time').values('start_time')[:1]

        next_session_qs = Session.objects.filter(
            client=user,
            psychologist=OuterRef('pk'),
            start_time__gt=now()
        ).order_by('start_time').values('start_time')[:1]

        qs = PsychologistSurvey.objects.filter(
            session__client=user
        ).distinct().annotate(
            last_session=Subquery(last_session_qs, output_field=DateTimeField()),
            next_session=Subquery(next_session_qs, output_field=DateTimeField())
        )
        return qs


class TimeSlotViewSet(ModelViewSet):
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimeSlot.objects.filter(psychologist=self.request.user)

    def create(self, request, *args, **kwargs):

        time_slots = create_time_slot(request.user, request.data)
        serializer = self.get_serializer(time_slots, many=True)
        return Response(serializer.data, status=201)



class PsychologistScheduleAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, psychologist_id):
        psychologist = get_object_or_404(PsychologistSurvey, id=psychologist_id)

        if not Session.objects.filter(client=request.user, psychologist=psychologist).exists():
            return Response(
                {"detail": "У вас нет сессии с данным психологом."},
                status=403
            )

        timeslots = TimeSlot.objects.filter(psychologist=psychologist, is_available=True)

        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())

        week_slots = []
        for slot in timeslots:
            slot_date = start_of_week + timedelta(days=slot.day_of_week)

            occurrence = datetime.combine(slot_date, slot.time)
            week_slots.append({
                'slot_id': slot.id,
                'day_of_week': slot.get_day_of_week_display(),
                'time': slot.time.strftime('%H:%M'),
                'datetime': occurrence.strftime('%Y-%m-%d %H:%M')
            })

        week_slots.sort(key=lambda x: x['datetime'])
        return Response(week_slots)