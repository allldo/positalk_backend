from django.db.models import Model, CharField, DateTimeField, ImageField, TextField, PositiveIntegerField, \
    ManyToManyField, SlugField, ForeignKey, CASCADE, IntegerField
from pytils.translit import slugify
from tinymce.models import HTMLField


class Article(Model):
    AGE_CHOICES = [
        (16, "16+"),
        (18, "18+"),
    ]
    title = CharField(max_length=125, verbose_name="Название")
    author = CharField(max_length=125, verbose_name="Автор")
    slug = SlugField(max_length=275, unique=True, blank=True, verbose_name="Слаг")
    date_created = DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    description = HTMLField(verbose_name="Описание")
    cover = ImageField(upload_to='article_covers/', null=True, blank=True , verbose_name="Обложка")
    full_image = ImageField(upload_to='article_full_images/', null=True, blank=True , verbose_name="Полная картинка")
    body = ManyToManyField("Block", null=True, blank=True , related_name="articles",verbose_name="Тело статьи")
    age_restriction = PositiveIntegerField(
        choices=AGE_CHOICES,
        null=True, blank=True , verbose_name="Ограничение по возрасту"
    )
    # Возможность планирования статьи
    release_datetime = DateTimeField(null=True, blank=True , verbose_name="Время выпуска статьи")
    time_for_reading = CharField(max_length=150 , verbose_name="Время на прочтение")
    related_articles = ManyToManyField("Article", null=True, blank=True , verbose_name="Похожие статьи")

    class Meta:
        ordering = ['-date_created']
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)
        if self.release_datetime is None:
            self.release_datetime = self.date_created
            self.save()

    def __str__(self):
        return self.title


class Test(Model):
    CALCULATION_CHOICES = [
        ("point", "По баллам"),
        ("position", "По порядковому номеру ответов"),
    ]
    TEST_TYPE_CHOICES = [
        (1, "Первый"),
        (2, "Второй"),
        (3, "Третий"),

        (4, "Четвертый"),

        (5, "Пятый"),
    ]
    slug = SlugField(max_length=275, unique=True, blank=True)
    title = CharField(max_length=125, verbose_name="Название")
    description = HTMLField(verbose_name="Описание")
    second_description = HTMLField(null=True, blank=True, verbose_name="Описание 2 (для тестов 3 типа)")
    cover = ImageField(upload_to='test_covers/', null=True, blank=True, verbose_name="Обложка")
    full_image = ImageField(upload_to='test_full_images/', null=True, blank=True, verbose_name="Полная картинка")
    calculation = CharField(max_length=50, choices=CALCULATION_CHOICES, verbose_name="Подсчет")
    questions = ManyToManyField("Question", verbose_name="Вопросы", related_name="tests")
    time_for_solving = CharField(max_length=75, default="20 минут", verbose_name="Время на решение")
    test_type = IntegerField(choices=TEST_TYPE_CHOICES, default=1, verbose_name="Тип теста")

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Test, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"


class Question(Model):
    title = HTMLField(null=True, blank=True, verbose_name="Название")
    scale = CharField(max_length=225, null=True, blank=True)
    image = ImageField(upload_to='question_images/', null=True, blank=True, verbose_name="Картинка")
    answers = ManyToManyField("Answer", blank=True, verbose_name="Ответы")

    def __str__(self):
        return f"{self.title}"
    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"


class Answer(Model):
    title = CharField(max_length=550, null=True, blank=True, verbose_name="Название")
    image = ImageField(upload_to='answer_images/', null=True, blank=True, verbose_name="Картинка")
    points = IntegerField(default=0, verbose_name="Количество баллов")
    ideal_score = IntegerField(default=5, null=True, blank=True)

    def __str__(self):
        return f"{self.title}"
    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"


class Result(Model):
    test = ForeignKey("Test", on_delete=CASCADE, verbose_name="Тест")
    description = HTMLField(null=True, blank=True, verbose_name="Описание")
    cover = ImageField(upload_to='result_covers/', null=True, blank=True, verbose_name="Обложка")
    min_points = IntegerField(null=True, blank=True, verbose_name="Минимальное кол-во очков")
    max_points = IntegerField(null=True, blank=True, verbose_name="Максимальное кол-во очков")
    position = IntegerField(null=True, blank=True, verbose_name="Позиция")

    def __str__(self):
        return f"Результат для теста: {self.test.title}, id : {self.id}"

    class Meta:
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестов"


class Block(Model):
    title = CharField(max_length=275, null=True, blank=True, verbose_name="Название")
    description = HTMLField(null=True,blank=True, verbose_name="Описание")

    def __str__(self):
        return self.title if self.title else str(self.id)

    class Meta:
        verbose_name = "Блок"
        verbose_name_plural = "Блоки"


class Feeling(Model):
    name = CharField(max_length=255, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Мое состояние"
        verbose_name_plural = "Мое состояние"


class Relation(Model):
    name = CharField(max_length=255, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Отношения"
        verbose_name_plural = "Отношения"


class WorkStudy(Model):
    name = CharField(max_length=255, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Учеба и работа"
        verbose_name_plural = "Учеба и работа"


class LifeEvent(Model):
    name = CharField(max_length=255, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "События в жизни"
        verbose_name_plural = "События в жизни"


class CoupleTherapy(Model):
    name = CharField(max_length=255, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Парная терапия"
        verbose_name_plural = "Парная терапия"


class PreferablePrice(Model):
    price = IntegerField(default=0, verbose_name="Цена")
    experience = CharField(max_length=225, null=True, blank=True, verbose_name="Опыт")
    description = TextField(blank=True, verbose_name="Описание")
    specialists_num = IntegerField(default=0, verbose_name="Количество специалистов")
    therapy_type = CharField(max_length=225, null=True, blank=True, verbose_name="Тип терапии")

    def __str__(self):
        return f"{self.price}Р и {self.specialists_num} специалистов"

    class Meta:
        verbose_name = "Предпочитаемая цена"
        verbose_name_plural = "Предпочитаемые цены"

class PsychoTopic(Model):
    name = CharField(max_length=255, verbose_name="Название")

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "Психологическая тема"
        verbose_name_plural = "Психологическые темы"
