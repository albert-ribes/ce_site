# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-30 10:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ce_availability', '0016_auto_20180130_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='kindofday',
            name='comment',
            field=models.CharField(blank=True, max_length=41),
        ),
    ]
