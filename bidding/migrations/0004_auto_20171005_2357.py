# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-05 18:27
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bidding', '0003_auto_20171005_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seller',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='seller', to=settings.AUTH_USER_MODEL),
        ),
    ]
