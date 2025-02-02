# Generated by Django 4.2.16 on 2025-01-13 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cabinet', '0007_customuser_user_type_alter_survey_couple_therapy_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField(default=2000)),
                ('text', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='psychologistsurvey',
            name='education',
        ),
        migrations.AddField(
            model_name='psychologistsurvey',
            name='age',
            field=models.PositiveIntegerField(blank=True, default=18, null=True),
        ),
        migrations.AddField(
            model_name='psychologistsurvey',
            name='label',
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
        migrations.AddField(
            model_name='psychologistsurvey',
            name='rating',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=2, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('user', 'user'), ('psychologist', 'psychologist')], default='user', max_length=225),
        ),
        migrations.AlterField(
            model_name='psychologistsurvey',
            name='experience',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='psychologistsurvey',
            name='name',
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
        migrations.AddField(
            model_name='psychologistsurvey',
            name='education_psychologist',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cabinet.education'),
        ),
    ]
