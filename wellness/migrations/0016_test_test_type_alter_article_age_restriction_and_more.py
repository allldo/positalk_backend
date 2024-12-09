# Generated by Django 4.2.16 on 2024-12-09 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wellness', '0015_alter_article_options_alter_test_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='test_type',
            field=models.IntegerField(choices=[(1, 1)], default=1, verbose_name='Тип теста'),
        ),
        migrations.AlterField(
            model_name='article',
            name='age_restriction',
            field=models.PositiveIntegerField(blank=True, choices=[(16, '16+'), (18, '18+')], null=True, verbose_name='Ограничение по возрасту'),
        ),
        migrations.AlterField(
            model_name='result',
            name='description',
            field=models.TextField(verbose_name='Описание'),
        ),
    ]
