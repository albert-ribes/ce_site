# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-20 16:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ce_availability', '0023_auto_20180220_1612'),
    ]

    operations = [
        migrations.RenameField(
            model_name='register',
            old_name='created_by',
            new_name='createdby',
        ),
    ]