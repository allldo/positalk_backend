from datetime import date, datetime, timedelta, time as dt_time

import pytz
from celery.bin.control import status
from django.conf import settings
from django.db.models import OuterRef, Subquery, DateTimeField, Count, Q
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView, get_object_or_404, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from cabinet.models import PsychologistSurvey, Survey
from session.models import TimeSlot, Session, Chat, Message, Connection
from session.paginators import MessagePagination
from session.permissions import IsPsychologist
from session.serializers import TimeSlotSerializer, PsychologistSessionSerializer, SessionDateSerializer, \
    PsychologistClientSerializer, ChatPsychologistSerializer, ChatClientSerializer, MessageSerializer, \
    CreateChatSerializer
from session.service import create_time_slot, is_time_slot_available


class PsychologistSessionListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = PsychologistSessionSerializer

    def get_queryset(self):
        user = self.request.user
        survey = Survey.objects.filter(user=user).first()
        last_session_qs = Session.objects.filter(
            client=user,
            psychologist=OuterRef('pk'),
            start_time__lt=now()
        ).exclude(status__in=['awaiting_payment', 'cancelled']).order_by('-start_time').values('start_time')[:1]

        next_session_qs = Session.objects.filter(
            client=user,
            psychologist=OuterRef('pk'),
            start_time__gt=now()
        ).exclude(status__in=['awaiting_payment', 'cancelled']).order_by('start_time').values('start_time')[:1]

        qs = PsychologistSurvey.objects.filter(connection__client=survey,
                                               connection__is_active=True,
                                               is_approved=True).distinct().annotate(
            last_session=Subquery(last_session_qs, output_field=DateTimeField()),
            next_session=Subquery(next_session_qs, output_field=DateTimeField())
        )
        return qs


class TimeSlotViewSet(ModelViewSet):
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimeSlot.objects.filter(psychologist=self.request.user.get_psychologist())

    def create(self, request, *args, **kwargs):

        time_slots = create_time_slot(request.user, request.data)
        if time_slots.get('error'):
            return Response(time_slots, status=400)
        serializer = self.get_serializer(time_slots, many=True)
        return Response(serializer.data, status=201)


class ClientHasAPIView(APIView):
    def get(self, request, psychologist_id):
        psychologist = get_object_or_404(PsychologistSurvey, id=psychologist_id)

        if not Session.objects.filter(client=request.user, psychologist=psychologist, status='awaiting').exists():
            return Response(
                {"status": "False"},
                status=200
            )

        return Response(data={'status': 'True'}, status=200)


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

        # if not Session.objects.filter(client=request.user, psychologist=psychologist, status='awaiting').exists():
        #     return Response(
        #         {"detail": "У вас нет сессии с данным психологом."},
        #         status=403
        #     )
        survey = Survey.objects.filter(user=request.user).first()
        client_tz = pytz.timezone(survey.timezone)
        psychologist_tz = pytz.timezone(psychologist.timezone)
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

        start_dt = psychologist_tz.localize(datetime.combine(start_date, dt_time.min))
        end_dt = psychologist_tz.localize(datetime.combine(end_date + timedelta(days=1), dt_time.min))
        sessions = Session.objects.filter(
            psychologist=psychologist,
            start_time__gte=start_dt,
            start_time__lt=end_dt,
            status='awaiting'
        )

        session_id = None
        session_dict = {session.start_time.astimezone(psychologist_tz).strftime('%Y-%m-%d %H:%M'): session for session
                        in sessions}

        occurrences = []
        current_date = start_date
        while current_date <= end_date:
            for slot in timeslots:
                if current_date.weekday() == slot.day_of_week:
                    occurrence_dt = psychologist_tz.localize(datetime.combine(current_date, slot.time))
                    occurrence_dt_client = occurrence_dt.astimezone(client_tz)
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
                        'day_of_week': settings.DAYS_RU[occurrence_dt_client.strftime('%A')],
                        'time': occurrence_dt_client.strftime('%H:%M'),
                        'datetime': occurrence_dt_client.strftime('%Y-%m-%d %H:%M'),
                        'status': status_slot,
                        'session_id': session_id
                    })
            current_date += timedelta(days=1)

        occurrences.sort(key=lambda x: x['datetime'])
        response = {'slots': occurrences, 'psychologist_info':
            {'psychologist_name': psychologist.name,'psychologist_avatar': f"{settings.CURRENT_DOMAIN}{psychologist.photo.url}" },
             'session_duration': psychologist.session_duration}
        return Response(response)


class MyScheduleRangeAPIView(APIView):
    """
    Ожидаемые GET-параметры (формат даты: YYYY-MM-DD):
      - start_date: начало диапазона (если не указан, по умолчанию сегодня);
      - end_date: конец диапазона (если не указан, по умолчанию через 7 дней от start_date).
    """
    permission_classes = [IsAuthenticated, IsPsychologist]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        print(self.request.user.id)
        psychologist = get_object_or_404(PsychologistSurvey, user__id=self.request.user.id)

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

        ).exclude(status__in=['awaiting_payment', 'cancelled'])

        session_dict = {}
        session_id = None
        for session in sessions:
            key = session.start_time.strftime('%Y-%m-%d %H:%M')
            session_dict[key] = session

        occurrences = []
        current_date = start_date
        while current_date <= end_date:
            session = None

            for slot in timeslots:
                if current_date.weekday() == slot.day_of_week:
                    occurrence_dt = datetime.combine(current_date, slot.time)
                    occ_str = occurrence_dt.strftime('%Y-%m-%d %H:%M')
                    status_slot = "free"
                    client_id = None
                    if occ_str in session_dict:
                        session = session_dict[occ_str]
                        session_id = session.id
                        client_id = session.client.id
                        status_slot = "busy"

                    occurrences.append({
                        'slot_id': slot.id,
                        'day_of_week': slot.get_day_of_week_display(),
                        'time': slot.time.strftime('%H:%M'),
                        'datetime': occ_str,
                        'status': status_slot,
                        'client_id': client_id,
                        'session_id': session_id,
                        'client_name': session.client.get_name() if session else None
                    })
                    session_id = None
                    session = None
            current_date += timedelta(days=1)

        occurrences.sort(key=lambda x: x['datetime'])
        response = {'slots': occurrences, 'session_duration': psychologist.session_duration}
        return Response(response)


class TransferSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # нужны проверки: на прошлое, 24 часа
    @extend_schema(request=SessionDateSerializer)
    def post(self, request, session_id):
        session = Session.objects.get(id=session_id, client=request.user, status='awaiting')
        serializer = SessionDateSerializer(data=request.data)
        reason = ""
        if serializer.is_valid():
            is_available, reason = is_time_slot_available(session.psychologist, serializer.data.get('start_time'), serializer.data.get('end_time'),
                               request.user)

            if is_available:
                psychologist_tz = pytz.timezone(session.psychologist.timezone)  # Часовой пояс психолога
                start_time_utc = datetime.strptime(serializer.data.get('start_time').rstrip("Z"),
                                                   "%Y-%m-%dT%H:%M:%S").replace(tzinfo=pytz.utc)
                end_time_utc = datetime.strptime(serializer.data.get('end_time').rstrip("Z"),
                                                 "%Y-%m-%dT%H:%M:%S").replace(tzinfo=pytz.utc)
                start_time_psychologist = start_time_utc.astimezone(psychologist_tz)
                end_time_psychologist = end_time_utc.astimezone(psychologist_tz)
                session.start_time = start_time_psychologist
                session.end_time = end_time_psychologist
                session.save()
                return Response(data={'status': 'success'}, status=200)

        return Response(data={'status': 'fail', 'reason': reason}, status=400)


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
        reason = ""
        if serializer.is_valid():
            is_available, reason = is_time_slot_available(psychologist, serializer.data.get('start_time'), serializer.data.get('end_time'),
                                   request.user)
            if is_available:
                session = Session.objects.create(psychologist=psychologist,
                                       client=request.user, start_time = serializer.data.get('start_time'),
                                       end_time = serializer.data.get('end_time'), status='awaiting_payment')

                return Response(data={'status': 'success', "session_id": session.id}, status=200)
        return Response(data={'status': 'fail', 'reason': reason}, status=200)


class MyClientsListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsPsychologist]
    authentication_classes = [TokenAuthentication]
    serializer_class = PsychologistClientSerializer

    def get_queryset(self):
        psychologist = self.request.user.get_psychologist()

        if not psychologist:
            return PsychologistSurvey.objects.none()

        # Подзапрос для даты последней сессии
        last_session_qs = Session.objects.filter(
            client=OuterRef('user'),
            psychologist=psychologist,
            start_time__lt=now()
        ).order_by('-start_time').values('start_time')[:1]

        # Подзапрос для даты следующей сессии
        future_session_qs = Session.objects.filter(
            client=OuterRef('user'),
            psychologist=psychologist,
            start_time__gt=now()
        ).order_by('start_time').values('start_time')[:1]

        # Основной запрос
        return PsychologistSurvey.objects.filter(
            user__sessions__psychologist=psychologist
        ).distinct().annotate(
            session_count=Count('user__sessions'),
            last_session_date=Subquery(last_session_qs, output_field=DateTimeField()),
            future_session_date=Subquery(future_session_qs, output_field=DateTimeField())
        )


class MyBusyScheduleRangeAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsPsychologist]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        psychologist = get_object_or_404(PsychologistSurvey, user__id=self.request.user.id)

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
            session = None
            for slot in timeslots:
                if current_date.weekday() == slot.day_of_week:
                    occurrence_dt = datetime.combine(current_date, slot.time)
                    occ_str = occurrence_dt.strftime('%Y-%m-%d %H:%M')
                    status_slot = "free"
                    if occ_str in session_dict:
                        session = session_dict[occ_str]
                        session_id = session.id
                        status_slot = "busy"

                    occurrences.append({
                        'slot_id': slot.id,
                        'day_of_week': slot.day_of_week,
                        'time': slot.time.strftime('%H:%M'),
                        'datetime': occ_str,
                        'status': status_slot,
                        'session_id': session_id,
                        'client_name': session.client.get_name() if session else None
                    })
            current_date += timedelta(days=1)

        occurrences.sort(key=lambda x: x['datetime'])
        response = {'slots': occurrences, 'session_duration': psychologist.session_duration}
        return Response(response)


class ChatListAPIView(ListAPIView):
    # serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def list(self, request, *args, **kwargs):
        if self.request.user.user_type == 'psychologist':
            return Response(ChatPsychologistSerializer(Chat.objects.filter(psychologist=self.request.user), many=True).data)
        if self.request.user.user_type == 'user':
            return Response(ChatClientSerializer(Chat.objects.filter(client=self.request.user), many=True).data)
        return Response(data={"message": "Chats not found"}, status=404)


class MessageListAPIView(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = MessagePagination

    def get_queryset(self):
        return Message.objects.filter(chat=self.kwargs['chat_id']).order_by('-created_at')


class CreateChatAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = CreateChatSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat = Chat.objects.filter(**serializer.validated_data).first()
        if not chat:
            chat = Chat.objects.create(**serializer.validated_data)
        return Response(CreateChatSerializer(chat).data)


class CancelConnectionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, connection_id):
        try:
            survey = Survey.objects.filter(user=request.user).first()
            connection = get_object_or_404(Connection, id=connection_id, client=survey, is_active=True)
            connection.is_active = False
            connection.save()
            return Response(data={'status': 'success'}, status=200)

        except Exception as e:
            print(e)
            return Response(data={'status': 'fail', 'reason': str(e)}, status=400)