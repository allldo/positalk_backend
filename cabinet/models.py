import random
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, DateTimeField, BooleanField, EmailField, ForeignKey, CASCADE
from django.utils.timezone import now, timedelta

from cabinet.managers import UserManager


class CustomUser(AbstractUser):
    # REQUIRED_FIELDS = []
    username = None
    objects = UserManager()
    phone_number = CharField(max_length=30,unique=True, null=True, blank=True, verbose_name='Номер телефона')
    USERNAME_FIELD = 'phone_number'


class PhoneVerification(Model):
    phone = CharField(max_length=15, verbose_name="Номер телефона")
    code = CharField(max_length=6, verbose_name="Код")
    created_at = DateTimeField(auto_now_add=True)
    is_active = BooleanField(default=True)

    def is_valid(self):
        return self.created_at > now() - timedelta(minutes=5)

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))


class Survey(Model):
    user = ForeignKey(CustomUser, on_delete=CASCADE, related_name="profile")
    nickname = CharField(max_length=225, null=True, blank=True)
    had_therapy_before = BooleanField(default=False)
    date_of_birth = CharField(max_length=128, null=True, blank=True)
    email = EmailField(unique=True, null=True, blank=True)
    promo_code = CharField(max_length=225, null=True, blank=True)
    feeling = CharField(max_length=225, null=True, blank=True)
    relation = CharField(max_length=225, null=True, blank=True)
    work_study = CharField(max_length=225, null=True, blank=True)
    life_event = CharField(max_length=225, null=True, blank=True)