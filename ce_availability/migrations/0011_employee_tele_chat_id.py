# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-12-15 20:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ce_availability', '0010_location_loc_short'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='tele_chat_id',
            field=models.IntegerField(blank=True, default=1),
        ),
    ]