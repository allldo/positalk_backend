# Generated by Django 4.2.16 on 2025-02-20 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0021_remove_psychologistsurvey_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='education',
            name='diploma',
            field=models.FileField(blank=True, null=True, upload_to='education_diplomas/', verbose_name='Файл об образовании'),
        ),
        migrations.AddField(
            model_name='psychologistsurvey',
            name='contract',
            field=models.FileField(blank=True, null=True, upload_to='contract_files/'),
        ),
        migrations.AddField(
            model_name='psychologistsurvey',
            name='inn_file',
            field=models.FileField(blank=True, null=True, upload_to='inn_files/'),
        ),
        migrations.AddField(
            model_name='psychologistsurvey',
            name='passport',
            field=models.FileField(blank=True, null=True, upload_to='passport_files/'),
        ),
        migrations.AddField(
            model_name='psychologistsurvey',
            name='registration',
            field=models.FileField(blank=True, null=True, upload_to='registration_files/'),
        ),
        migrations.AddField(
            model_name='psychologistsurvey',
            name='retirement_certificate',
            field=models.FileField(blank=True, null=True, upload_to='retirement_certificate_files/'),
        ),
    ]
