import random
from random import choice

from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, DateTimeField, BooleanField, EmailField, ForeignKey, CASCADE, SET_NULL, \
    ManyToManyField, PositiveIntegerField, TextField, ImageField, DecimalField
from django.utils.timezone import now, timedelta

from cabinet.managers import UserManager


class CustomUser(AbstractUser):
    # REQUIRED_FIELDS = []
    USER_TYPE_CHOICES = [
        ('user', 'user'),
        ('psychologist', 'psychologist'),
    ]
    username = None
    objects = UserManager()
    phone_number = CharField(max_length=30,unique=True, null=True, blank=True, verbose_name='Номер телефона')
    USERNAME_FIELD = 'phone_number'
    user_type = CharField(max_length=225, choices=USER_TYPE_CHOICES, default='user')
    def __str__(self):
        return self.phone_number if self.phone_number else str(self.id)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class PhoneVerification(Model):
    phone = CharField(max_length=15, verbose_name="Номер телефона")
    code = CharField(max_length=6, verbose_name="Код")
    created_at = DateTimeField(auto_now_add=True)
    is_active = BooleanField(default=True, verbose_name="Активный код")

    def __str__(self):
        return f"{self.phone} - {self.is_active}"

    def is_valid(self):
        return self.created_at > now() - timedelta(minutes=5)

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

    class Meta:
        verbose_name = "Коды смс"
        verbose_name_plural = "Коды смс"


class Education(Model):
    year = PositiveIntegerField(default=2000, verbose_name="Год выпуска")
    text = TextField(verbose_name="Университет")

    def __str__(self):
        return f"Год выпуска - {self.year}"

    class Meta:
        ordering = ['-year']
        verbose_name = "Образование"
        verbose_name_plural = "Образование"


class Survey(Model):
    user = ForeignKey(CustomUser, on_delete=CASCADE, related_name="profile", verbose_name="Пользователь")
    therapy_type = CharField(max_length=225, null=True, blank=True, verbose_name="Тип терапии")
    nickname = CharField(max_length=225, null=True, blank=True, verbose_name="Псевдоним")
    had_therapy_before = BooleanField(default=False, verbose_name="Был опыт терапии?")
    date_of_birth = CharField(max_length=128, null=True, blank=True, verbose_name="Дата рождения")
    email = EmailField(unique=True, null=True, blank=True, verbose_name="Эл. почта")
    promo_code = CharField(max_length=225, null=True, blank=True, verbose_name="Промокод")
    feeling = ManyToManyField("wellness.Feeling", blank=True, related_name='feeling', verbose_name="Мое состояние")
    relation = ManyToManyField("wellness.Relation", blank=True, related_name='relation', verbose_name="Отношения")
    work_study = ManyToManyField("wellness.WorkStudy", blank=True, related_name='work_study', verbose_name="Учеба и работа")
    life_event = ManyToManyField("wellness.LifeEvent", blank=True, related_name='life_event', verbose_name="События в жизни")
    couple_therapy = ManyToManyField("wellness.CoupleTherapy", blank=True, related_name='couple_therapy', verbose_name="Парная терапия")
    preferable_price = ForeignKey("wellness.PreferablePrice", on_delete=SET_NULL, null=True, blank=True, verbose_name="Предпочитаемая цена")

    def __str__(self):
        return f"Анкета {self.nickname}, тип терапии {self.therapy_type}"

    class Meta:
        verbose_name = "Анкета"
        verbose_name_plural = "Анкеты"


class PsychologistSurvey(Model):
    SEX_CHOICES = [
        ('woman', 'Женский'),
        ('man', 'Мужской')
    ]

    photo = ImageField(upload_to='psycho_avatars/', null=True, blank=True, verbose_name="Фото")
    user = ForeignKey(CustomUser, on_delete=CASCADE, related_name="psycho_profile", verbose_name="Пользователь")
    education_psychologist = ManyToManyField(Education, blank=True, verbose_name="Образование")
    name = CharField(max_length=225, null=True, blank=True, verbose_name="Имя")
    age = PositiveIntegerField(default=18, null=True, blank=True, verbose_name="Возраст")
    label = CharField(max_length=225, null=True, blank=True, verbose_name="Подпись")
    experience = PositiveIntegerField(null=True, blank=True, verbose_name="Опыт")
    rating = DecimalField(max_digits=2,decimal_places=1, null=True, blank=True, verbose_name="Рейтинг")
    psycho_topic = ManyToManyField("wellness.PsychoTopic", verbose_name="Направление")
    description = TextField(verbose_name="Описание")
    sex = CharField(max_length=125, choices=SEX_CHOICES, default='man', verbose_name="Пол")

    def __str__(self):
        return f"Психолог {self.name}, опыт {self.experience}, рейтинг - {self.rating}"

    class Meta:
        verbose_name = "Психолог"
        verbose_name_plural = "Психологи"