# Generated by Django 4.2.16 on 2024-12-11 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wellness', '0024_remove_result_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='ideal_score',
            field=models.IntegerField(blank=True, default=5, null=True),
        ),
    ]
