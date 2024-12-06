from django.db.models import Model, CharField, DateTimeField, ImageField, TextField, PositiveIntegerField, \
    ManyToManyField, SlugField
from pytils.translit import slugify

class Article(Model):
    AGE_CHOICES = {
        (16, "16+"),
        (18, "18+"),
    }
    title = CharField(max_length=125)
    author = CharField(max_length=125)
    slug = SlugField(max_length=275, unique=True, blank=True)
    date_created = DateTimeField(auto_now_add=True)
    description = CharField(max_length=550)
    cover = ImageField(upload_to='article_covers/', null=True, blank=True)
    full_image = ImageField(upload_to='article_full_images/', null=True, blank=True)
    body = ManyToManyField("Block", null=True, blank=True)
    age_restriction = PositiveIntegerField(
        choices=AGE_CHOICES,
        null=True, blank=True
    )
    # Возможность планирования статьи
    release_datetime = DateTimeField(null=True, blank=True)
    time_for_reading = CharField(max_length=150)
    related_articles = ManyToManyField("Article", null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Article, self).save(*args, **kwargs)
        if self.release_datetime is None:
            self.release_datetime = self.date_created
            self.save()

class Test(Model):
    CALCULATION_CHOICES = {
        ("point", "По баллам"),
        ("position", "По порядковому номеру ответов"),
    }
    title = CharField(max_length=125)
    description = CharField(max_length=550)
    cover = ImageField(upload_to='test_covers/', null=True, blank=True)
    calculation = CharField(max_length=50, choices=CALCULATION_CHOICES)
    questions = ManyToManyField("Question")


class Question(Model):
    title = CharField(max_length=550, null=True, blank=True)
    image = ImageField(upload_to='question_images/', null=True, blank=True)
    answers = ManyToManyField("Answer", blank=True)


class Answer(Model):
    title = CharField(max_length=550, null=True, blank=True)
    image = ImageField(upload_to='answer_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.title}"


class Block(Model):
    title = CharField(max_length=275)
    description = TextField()

    def __str__(self):
        return self.title