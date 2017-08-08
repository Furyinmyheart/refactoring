# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-23 12:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stantions', '0006_auto_20170222_1028'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='stantion',
            managers=[
            ],
        ),
        migrations.AddField(
            model_name='expert',
            name='api_key',
            field=models.CharField(blank=True, max_length=255, verbose_name='Ключ для API'),
        ),
        migrations.AddField(
            model_name='expert',
            name='interface',
            field=models.CharField(blank=True, choices=[('eaisto', 'ЕАИСТО')], max_length=255, verbose_name='Интерфейс'),
        ),
        migrations.AddField(
            model_name='expert',
            name='interface_url',
            field=models.URLField(blank=True, max_length=255, verbose_name='Интерфейс url'),
        ),
        migrations.AddField(
            model_name='stantion',
            name='interface_url',
            field=models.URLField(blank=True, max_length=255, verbose_name='Интерфейс url'),
        ),
    ]
