from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField


class CustomUser(AbstractUser):
    # REQUIRED_FIELDS = []
    # USERNAME_FIELD = 'phone_number'
    phone_number = CharField(max_length=30, null=True, blank=True, verbose_name='Номер телефона')
