# Generated by Django 4.2.16 on 2024-12-06 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wellness', '0003_alter_test_calculation'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='slug',
            field=models.SlugField(blank=True, max_length=275, unique=True),
        ),
    ]