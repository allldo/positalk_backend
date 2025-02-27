import random

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, CharField, DateTimeField, BooleanField, EmailField, ForeignKey, CASCADE, SET_NULL, \
    ManyToManyField, PositiveIntegerField, TextField, ImageField, DecimalField, DurationField, TimeField, DateField, \
    FileField
from django.utils.timezone import now, timedelta
from datetime import date
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

    def get_name(self):
        if self.user_type == 'user':
            survey = Survey.objects.filter(user=self).first()
            try:
                return survey.nickname
            except AttributeError:
                return "Без псевдонима"
        if self.user_type == 'psychologist':
            psychologist = self.get_psychologist()
            if psychologist:
                return psychologist.name
        return None

    def get_psychologist(self):
        try:
            return PsychologistSurvey.objects.filter(user=self).first()
        except PsychologistSurvey.DoesNotExist:
            return None

    def get_psychologist_name(self):
        psychologist = self.get_psychologist()
        if psychologist:
            return psychologist.name
        return "Без псевдонима"

    def get_psychologist_avatar(self):
        psychologist = self.get_psychologist()
        if psychologist:
            return f"{settings.CURRENT_DOMAIN}{psychologist.photo.url}" if psychologist.photo else ""
        return ""

    def get_avatar(self):
        if self.user_type == 'user':
            survey = Survey.objects.filter(user=self).first()
            return f"{settings.CURRENT_DOMAIN}{survey.photo.url}" if survey.photo else ""


class PhoneVerification(Model):
    phone = CharField(max_length=19, verbose_name="Номер телефона")
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
    diploma = FileField(upload_to='education_diplomas/', null=True, blank=True, verbose_name="Файл об образовании")

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
    photo = ImageField('client_photos/', null=True, blank=True,)
    had_therapy_before = BooleanField(default=False, verbose_name="Был опыт терапии?")
    date_of_birth = DateField(null=True, blank=True, verbose_name="Дата рождения")
    email = EmailField(unique=True, null=True, blank=True, verbose_name="Эл. почта")
    promo_code = CharField(max_length=225, null=True, blank=True, verbose_name="Промокод")
    feeling = ManyToManyField("wellness.Feeling", blank=True, related_name='feeling', verbose_name="Мое состояние")
    relation = ManyToManyField("wellness.Relation", blank=True, related_name='relation', verbose_name="Отношения")
    work_study = ManyToManyField("wellness.WorkStudy", blank=True, related_name='work_study', verbose_name="Учеба и работа")
    life_event = ManyToManyField("wellness.LifeEvent", blank=True, related_name='life_event', verbose_name="События в жизни")
    couple_therapy = ManyToManyField("wellness.CoupleTherapy", blank=True, related_name='couple_therapy', verbose_name="Парная терапия")
    preferable_price = ForeignKey("wellness.PreferablePrice", on_delete=SET_NULL, null=True, blank=True, verbose_name="Предпочитаемая цена")

    timezone = CharField(max_length=225, default='Europe/Moscow', null=True, blank=True, verbose_name="Часовой пояс")

    news_notification = BooleanField(default=False, verbose_name="Уведомления о новостях")
    reminder_notification = BooleanField(default=False, verbose_name="Уведомления о встрече за 24 часа")
    message_notification = BooleanField(default=False, verbose_name="Уведомления о сообщении от терапевта")

    # if couple therapy
    nickname_second = CharField(max_length=225, null=True, blank=True, verbose_name="Псевдоним")
    photo_second = ImageField('client_photos/', null=True, blank=True,)
    date_of_birth_second = DateField(null=True, blank=True, verbose_name="Дата рождения")
    def __str__(self):
        return f"Анкета {self.nickname}, тип терапии {self.therapy_type} user {self.user.phone_number}"

    class Meta:
        verbose_name = "Анкета"
        verbose_name_plural = "Анкеты"


class PsychologistSurvey(Model):
    SEX_CHOICES = [
        ('woman', 'Женский'),
        ('man', 'Мужской')
    ]
    TAX_STATUS_CHOICES = [
        ('Самозанятый', 'Самозанятый'),
        ('ИП', 'ИП'),
        ('ООО', 'ООО'),
        ('АО', 'АО'),
    ]

    AGE_CLIENT_CHOICES = [
        ('16+', '16+'),
        ('18+', '18+'),
    ]

    photo = ImageField(upload_to='psycho_avatars/', null=True, blank=True, verbose_name="Фото")
    user = ForeignKey(CustomUser, on_delete=CASCADE, related_name="psycho_profile", verbose_name="Пользователь")
    education_psychologist = ManyToManyField(Education, blank=True, verbose_name="Образование")
    name = CharField(max_length=225, null=True, blank=True, verbose_name="Имя")
    age = PositiveIntegerField(null=True, blank=True, verbose_name="Возраст")
    label = CharField(max_length=225, null=True, blank=True, verbose_name="Подпись")
    experience = PositiveIntegerField(null=True, blank=True, verbose_name="Опыт")
    rating = DecimalField(max_digits=2,decimal_places=1, null=True, blank=True, verbose_name="Рейтинг")
    psycho_topic = ManyToManyField("wellness.PsychoTopic", blank=True, verbose_name="Направление")
    description = TextField(blank=True,verbose_name="Описание")
    sex = CharField(max_length=125, choices=SEX_CHOICES, default='man', verbose_name="Пол")
    price = PositiveIntegerField(default=0, verbose_name='Цена за сессию')
    email = EmailField(max_length=225, null=True, blank=True)

    notifications_phone = BooleanField(default=False)
    notifications_email = BooleanField(default=False)

    date_of_birth = DateField(null=True, blank=True)

    language = CharField(max_length=155, default='Русский')

    timezone = CharField(max_length=225, default="Europe/Moscow")
    session_duration = PositiveIntegerField(default=1, verbose_name="Длительность сессии") # в часах

    working_methods = TextField(blank=True)
    your_values = TextField(blank=True)
    how_get_profession = TextField(blank=True)
    couple_therapy = BooleanField(default=False)
    client_age = CharField(max_length=5, choices=AGE_CLIENT_CHOICES, default='18+')
    experience_with_identity_search = BooleanField(default=False)

    tax_status = CharField(max_length=225, choices=TAX_STATUS_CHOICES, null=True, blank=True)
    citizenship = CharField(max_length=225, default='РФ', null=True, blank=True)
    address = TextField(blank=True)
    inn = CharField(max_length=225, null=True, blank=True)

    accepted_to_system = BooleanField(default=False, verbose_name='Подписан/а в Позитолк')

    passport = FileField(upload_to='passport_files/', null=True, blank=True)
    registration = FileField(upload_to='registration_files/', null=True, blank=True)
    contract = FileField(upload_to='contract_files/', null=True, blank=True)
    inn_file = FileField(upload_to='inn_files/', null=True, blank=True)
    retirement_certificate = FileField(upload_to='retirement_certificate_files/', null=True, blank=True)

    is_approved = BooleanField(default=False, verbose_name='Одобрен/а')
    def __str__(self):
        # return f"Психолог {self.name}, опыт {self.experience}, рейтинг - {self.rating} - user {self.user}"
        return f"Психолог {self.name}; Одобрен" if self.is_approved else f"Психолог {self.name}; Не одобрен"
    class Meta:
        verbose_name = "Психолог"
        verbose_name_plural = "Психологи"

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            today = date.today()
            self.age = today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        super().save(*args, **kwargs)