import random
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, DateTimeField, BooleanField
from django.utils.timezone import now, timedelta

from cabinet.managers import UserManager


class CustomUser(AbstractUser):
    # REQUIRED_FIELDS = []
    # USERNAME_FIELD = 'phone_number'
    objects = UserManager()
    phone_number = CharField(max_length=30, null=True, blank=True, verbose_name='Номер телефона')


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