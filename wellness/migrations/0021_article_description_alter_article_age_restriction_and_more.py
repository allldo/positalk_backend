# Generated by Django 4.2.16 on 2024-12-09 12:49

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('wellness', '0020_remove_article_description_alter_test_calculation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='description',
            field=tinymce.models.HTMLField(default='', verbose_name='Описание'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='age_restriction',
            field=models.PositiveIntegerField(blank=True, choices=[(16, '16+'), (18, '18+')], null=True, verbose_name='Ограничение по возрасту'),
        ),
        migrations.AlterField(
            model_name='test',
            name='test_type',
            field=models.IntegerField(choices=[(1, 'Первый'), (2, 'Второй'), (3, 'Третий')], default=1, verbose_name='Тип теста'),
        ),
    ]
