# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-11 03:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DAGR', '0004_auto_20170510_1059'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='keyword',
            name='GUID',
        ),
        migrations.AddField(
            model_name='keyword',
            name='dagr',
            field=models.ManyToManyField(to='DAGR.DAGR'),
        ),
    ]
