# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2019-03-10 05:36
from __future__ import unicode_literals

from django.db import migrations, models


def mark_purged_locations(apps, schema_editor):
    DataLocation = apps.get_model("flow", "DataLocation")

    for data_location in DataLocation.objects.all():
        if data_location.data.filter(purged=True).exists():
            data_location.purged = True
            data_location.save()


class Migration(migrations.Migration):

    dependencies = [
        ("flow", "0032_add_collection_duplicate"),
    ]

    operations = [
        migrations.AddField(
            model_name="datalocation",
            name="purged",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(mark_purged_locations),
        migrations.RemoveField(model_name="data", name="purged",),
    ]
