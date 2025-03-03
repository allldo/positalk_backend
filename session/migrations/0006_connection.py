# Generated by Django 4.2.16 on 2025-02-26 18:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0026_survey_date_of_birth_second_and_more'),
        ('session', '0005_remove_message_is_read'),
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('date_started', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cabinet.survey')),
                ('psychologist', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cabinet.psychologistsurvey')),
            ],
        ),
    ]
