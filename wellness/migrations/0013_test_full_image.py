# Generated by Django 4.2.16 on 2024-12-07 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wellness', '0012_test_slug_alter_test_calculation'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='full_image',
            field=models.ImageField(blank=True, null=True, upload_to='test_full_images/'),
        ),
    ]
