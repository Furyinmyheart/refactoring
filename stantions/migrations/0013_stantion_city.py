# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-01 21:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_auto_20170301_2054'),
        ('stantions', '0012_remove_stantion_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='stantion',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.City', verbose_name='Город оператора'),
        ),
    ]
