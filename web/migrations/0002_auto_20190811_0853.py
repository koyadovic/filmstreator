# Generated by Django 2.2.3 on 2019-08-11 08:53

from django.db import migrations

from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition


def execute(apps, schema_editor):
    audiovisual_records = (
        Search.Builder
        .new_search(AudiovisualRecord)
        .add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
        .search()
    )
    for audiovisual_record in audiovisual_records:
        audiovisual_record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(execute)
    ]
