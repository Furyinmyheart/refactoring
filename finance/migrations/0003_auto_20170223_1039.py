# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-23 07:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_auto_20170223_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='user_parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions_user_parent', to=settings.AUTH_USER_MODEL),
        ),
    ]
