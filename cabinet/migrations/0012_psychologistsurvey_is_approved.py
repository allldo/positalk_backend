# Generated by Django 4.2.16 on 2025-02-09 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0011_psychologistsurvey_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='psychologistsurvey',
            name='is_approved',
            field=models.BooleanField(default=False, verbose_name='Одобрен/а'),
        ),
    ]
