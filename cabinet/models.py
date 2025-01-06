import random
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, DateTimeField, BooleanField, EmailField, ForeignKey, CASCADE, SET_NULL, \
    ManyToManyField
from django.utils.timezone import now, timedelta

from cabinet.managers import UserManager
from wellness.models import Feeling, Relation, WorkStudy, LifeEvent, CoupleTherapy


class CustomUser(AbstractUser):
    # REQUIRED_FIELDS = []
    username = None
    objects = UserManager()
    phone_number = CharField(max_length=30,unique=True, null=True, blank=True, verbose_name='Номер телефона')
    USERNAME_FIELD = 'phone_number'
    def __str__(self):
        return self.phone_number if self.phone_number else str(self.id)


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
    therapy_type = CharField(max_length=225, null=True, blank=True)
    nickname = CharField(max_length=225, null=True, blank=True)
    had_therapy_before = BooleanField(default=False)
    date_of_birth = CharField(max_length=128, null=True, blank=True)
    email = EmailField(unique=True, null=True, blank=True)
    promo_code = CharField(max_length=225, null=True, blank=True)
    feeling = ManyToManyField("wellness.Feeling", blank=True, related_name='feeling')
    relation = ManyToManyField("wellness.Relation", blank=True, related_name='relation')
    work_study = ManyToManyField("wellness.WorkStudy", blank=True, related_name='work_study')
    life_event = ManyToManyField("wellness.LifeEvent", blank=True, related_name='life_event')
    couple_therapy = ManyToManyField("wellness.CoupleTherapy", blank=True, related_name='couple_therapy')
    preferable_price = ForeignKey("wellness.PreferablePrice", on_delete=SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id)