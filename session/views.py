from datetime import date, datetime, timedelta, time as dt_time

from celery.bin.control import status
from django.conf import settings
from django.db.models import  OuterRef, Subquery, DateTimeField
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from cabinet.models import PsychologistSurvey
from session.models import TimeSlot, Session
from session.serializers import TimeSlotSerializer, PsychologistSessionSerializer, SessionDateSerializer
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
        ).exclude(status='awaiting_payment').order_by('-start_time').values('start_time')[:1]

        next_session_qs = Session.objects.filter(
            client=user,
            psychologist=OuterRef('pk'),
            start_time__gt=now()
        ).exclude(status='awaiting_payment').order_by('start_time').values('start_time')[:1]

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


class PsychologistScheduleRangeAPIView(APIView):
    """
    Ожидаемые GET-параметры (формат даты: YYYY-MM-DD):
      - start_date: начало диапазона (если не указан, по умолчанию сегодня);
      - end_date: конец диапазона (если не указан, по умолчанию через 7 дней от start_date).
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, psychologist_id):
        psychologist = get_object_or_404(PsychologistSurvey, id=psychologist_id)

        if not Session.objects.filter(client=request.user, psychologist=psychologist, status='awaiting').exists():
            return Response(
                {"detail": "У вас нет сессии с данным психологом."},
                status=403
            )

        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else date.today()
        except ValueError:
            return Response({"detail": "Неверный формат start_date. Ожидается YYYY-MM-DD."}, status=400)
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else start_date + timedelta(
                days=7)
        except ValueError:
            return Response({"detail": "Неверный формат end_date. Ожидается YYYY-MM-DD."}, status=400)

        timeslots = TimeSlot.objects.filter(psychologist=psychologist, is_available=True)

        start_dt = datetime.combine(start_date, dt_time.min)
        end_dt = datetime.combine(end_date + timedelta(days=1), dt_time.min)
        sessions = Session.objects.filter(
            psychologist=psychologist,
            start_time__gte=start_dt,
            start_time__lt=end_dt,
            status='awaiting'
        )

        session_dict = {}
        session_id = None
        for session in sessions:
            key = session.start_time.strftime('%Y-%m-%d %H:%M')
            session_dict[key] = session

        occurrences = []
        current_date = start_date
        while current_date <= end_date:
            for slot in timeslots:
                if current_date.weekday() == slot.day_of_week:
                    occurrence_dt = datetime.combine(current_date, slot.time)
                    occ_str = occurrence_dt.strftime('%Y-%m-%d %H:%M')
                    if occ_str in session_dict:
                        session = session_dict[occ_str]
                        if session.client == request.user:
                            status_slot = "busy_self"
                            session_id = session.id
                        else:
                            status_slot = "busy"
                    else:
                        status_slot = "free"
                    occurrences.append({
                        'slot_id': slot.id,
                        'day_of_week': slot.get_day_of_week_display(),
                        'time': slot.time.strftime('%H:%M'),
                        'datetime': occ_str,
                        'status': status_slot,
                        'session_id': session_id
                    })
            current_date += timedelta(days=1)

        occurrences.sort(key=lambda x: x['datetime'])
        response = {'slots': occurrences, 'psychologist_info':
            {'psychologist_name': psychologist.name,
             'psychologist_avatar': f"{settings.CURRENT_DOMAIN}{psychologist.photo.url}" }}
        return Response(response)


class TransferSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # нужны проверки: на прошлое, 24 часа
    @extend_schema(request=SessionDateSerializer)
    def post(self, request, session_id):
        session = Session.objects.get(id=session_id, client=request.user, status='awaiting')
        serializer = SessionDateSerializer(request.data)
        if serializer.is_valid():
            session.start_time = serializer.data.get('start_time')
            session.end_time = serializer.data.get('end_time')
            session.save()
            return Response(data={'status': 'success'}, status=200)


class CancelSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, session_id):
        session = Session.objects.get(id=session_id, client=request.user, status='awaiting')

        session.status = 'cancelled'
        session.save()
        return Response(data={'status': 'success'}, status=200)


class BookSessionAPIView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
# проверка на то была ли сессия с психологом (во избежание абуза)
    @extend_schema(request=SessionDateSerializer)
    def post(self, request, psychologist_id):
        psychologist = PsychologistSurvey.objects.get(id=psychologist_id)

        serializer = SessionDateSerializer(data=request.data)
        if serializer.is_valid():
            session = Session.objects.create(psychologist=psychologist,
                                   client=request.user, start_time = serializer.data.get('start_time'),
                                   end_time = serializer.data.get('end_time'), status='awaiting_payment')

            return Response(data={'status': 'success', "session_id": session.id}, status=200)
        return Response(data={'status': 'fail'}, status=200)