from django.db import models
from django.db.models import CharField, Model, ForeignKey, CASCADE, DateTimeField, TextField, BooleanField

from cabinet.models import PsychologistSurvey, CustomUser


class Session(models.Model):
    SESSION_CHOICES = [
        ('awaiting_payment', 'awaiting_payment'),
        ('cancelled', 'cancelled'),
        ('awaiting', 'awaiting'),
        ('complete', 'complete'),

    ]
    psychologist = models.ForeignKey(PsychologistSurvey, on_delete=models.CASCADE)
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sessions")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = CharField(max_length=225, choices=SESSION_CHOICES, default='awaiting_payment')

    def __str__(self):
        return f"{self.client} -> {self.psychologist} ({self.start_time})"


class TimeSlot(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    )

    psychologist = models.ForeignKey(
        PsychologistSurvey,
        on_delete=models.CASCADE,
        related_name='timeslots'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    time = models.TimeField(help_text="Время в формате HH:MM (от 00:00 до 23:00)")
    is_available = models.BooleanField(default=True, help_text="Доступен ли слот для записи")

    class Meta:
        unique_together = ('psychologist', 'day_of_week', 'time')
        ordering = ['day_of_week', 'time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.time} от {self.psychologist} ({'Доступен' if self.is_available else 'Не доступен'})"


class Chat(Model):
    client = ForeignKey(CustomUser, on_delete=CASCADE, related_name="client_chats")
    psychologist = ForeignKey(CustomUser, on_delete=CASCADE, related_name="psychologist_chats")
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {self.client} and {self.psychologist}"


class Message(Model):
    chat = ForeignKey(Chat, on_delete=CASCADE, related_name="messages")
    sender = ForeignKey(CustomUser, on_delete=CASCADE)
    text = TextField()
    created_at = DateTimeField(auto_now_add=True)
    # is_read = BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} at {self.created_at}"