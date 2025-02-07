# Generated by Django 2.2.3 on 2019-09-02 10:53

from django.db import migrations

from core.model.audiovisual import DownloadSourceResult
from core.model.searches import Search
from core.tools.strings import guess_language


def execute(apps, schema_editor):
    results = (
        Search.Builder
        .new_search(DownloadSourceResult)
        .search()
    )
    for result in results:
        if result.audiovisual_record is None:
            continue
        result.lang = guess_language(result.name)
        result.save()


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_auto_20190817_1748'),
    ]

    operations = [
        migrations.RunPython(execute)
    ]
