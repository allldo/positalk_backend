# Generated by Django 4.2.16 on 2025-02-23 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0024_psychologistsurvey_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='timezone',
            field=models.CharField(blank=True, default='Europe/Moscow', max_length=225, null=True, verbose_name='Часовой пояс'),
        ),
    ]
