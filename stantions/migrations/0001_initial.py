# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-09 18:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Expert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=255, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=255, verbose_name='Имя')),
                ('middle_name', models.CharField(max_length=255, verbose_name='Отчество')),
                ('eaisto_login', models.CharField(blank=True, max_length=255, verbose_name='Логин ЕАИСТО')),
                ('eaisto_password', models.CharField(blank=True, max_length=255, verbose_name='Пароль ЕАИСТО')),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(verbose_name='Активна')),
                ('order', models.IntegerField(verbose_name='№ в очереди на заполнение')),
                ('org_title', models.CharField(max_length=255, verbose_name='Организация')),
                ('reg_number', models.CharField(max_length=255, verbose_name='Рег. номер')),
                ('post_index', models.CharField(blank=True, max_length=255, verbose_name='Индекс оператора')),
                ('city', models.CharField(blank=True, max_length=255, verbose_name='Город оператора')),
                ('address', models.CharField(blank=True, max_length=255, verbose_name='Адрес оператора')),
                ('point_address', models.CharField(blank=True, max_length=255, verbose_name='Адрес пункта ТО')),
                ('eaisto_login', models.CharField(blank=True, max_length=255, verbose_name='Логин ЕАИСТО')),
                ('eaisto_password', models.CharField(blank=True, max_length=255, verbose_name='Пароль ЕАИСТО')),
                ('daily_limit', models.IntegerField(verbose_name='Дневной Лимит')),
            ],
        ),
        migrations.AddField(
            model_name='expert',
            name='stantion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stantions.Station', verbose_name='Пункт ТО'),
        ),
    ]