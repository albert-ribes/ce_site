# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-20 16:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ce_availability', '0002_remove_register_createdby'),
    ]

    operations = [
        migrations.AddField(
            model_name='register',
            name='createdby',
            field=models.ForeignKey(default=6, on_delete=django.db.models.deletion.CASCADE, related_name='CreatedByUser', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]