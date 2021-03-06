# Generated by Django 3.2.12 on 2022-04-14 20:19

from django.db import migrations, models
import uuid


def gen_uuid(apps, schema_editor):
    Source = apps.get_model("api", "Source")
    for row in Source.objects.all():
        row.external_id = uuid.uuid4()
        row.save(update_fields=["external_id"])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20220414_2018'),
    ]

    operations = [
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]
