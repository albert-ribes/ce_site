# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-20 10:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ce_overtime', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registerovertime',
            old_name='overtimereg',
            new_name='overtime',
        ),
    ]