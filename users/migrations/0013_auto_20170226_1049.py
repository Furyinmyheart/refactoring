# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 07:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20170225_1817'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='myuser',
            options={'ordering': ('fio', 'username'), 'permissions': (('can_create_admin', 'Может создавать администраторов'), ('can_create_agent', 'Может создавать агентов'), ('can_create_manager', 'Может создавать менеджеров'), ('can_move_child', 'Может перемещать агентов'), ('can_crud_child', 'Может редактировать своих агентов'), ('can_crud_all_child', 'Может редактировать своих агентов и агентов агентов'))},
        ),
    ]