# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-06 09:11
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='to_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='support_received', to=settings.AUTH_USER_MODEL, verbose_name='Кому'),
        ),
    ]