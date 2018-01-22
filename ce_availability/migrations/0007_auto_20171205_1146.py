# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-05 11:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ce_availability', '0006_delete_usertype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='register',
            name='end_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='register',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]