# Generated by Django 4.2.16 on 2025-01-06 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wellness', '0026_coupletherapy_feeling_lifeevent_preferableprice_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='preferableprice',
            name='therapy_type',
            field=models.CharField(blank=True, max_length=225, null=True),
        ),
        migrations.AlterField(
            model_name='preferableprice',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
