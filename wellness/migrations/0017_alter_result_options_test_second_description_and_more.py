# Generated by Django 4.2.16 on 2024-12-09 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wellness', '0016_test_test_type_alter_article_age_restriction_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='result',
            options={'verbose_name': 'Результат теста', 'verbose_name_plural': 'Результаты тестов'},
        ),
        migrations.AddField(
            model_name='test',
            name='second_description',
            field=models.TextField(default='', verbose_name='Описание 2 (для тестов 3 типа)'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='question',
            name='answers',
            field=models.ManyToManyField(blank=True, to='wellness.answer', verbose_name='Ответы'),
        ),
        migrations.AlterField(
            model_name='test',
            name='calculation',
            field=models.CharField(choices=[('point', 'По баллам'), ('position', 'По порядковому номеру ответов')], max_length=50, verbose_name='Подсчет'),
        ),
        migrations.AlterField(
            model_name='test',
            name='test_type',
            field=models.IntegerField(choices=[(2, 'Второй'), (1, 'Первый'), (3, 'Третий')], default=1, verbose_name='Тип теста'),
        ),
    ]
