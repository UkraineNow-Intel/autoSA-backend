# Generated by Django 3.2.12 on 2022-04-15 21:16

from django.db import migrations, models
import psqlextra.manager.manager


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20220414_2019'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='source',
            managers=[
                ('objects', psqlextra.manager.manager.PostgresManager()),
            ],
        ),
        migrations.AlterField(
            model_name='source',
            name='headline',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AlterField(
            model_name='source',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('ru', 'Russian'), ('ua', 'Ukrainian')], default='en', max_length=2),
        ),
        migrations.AlterField(
            model_name='source',
            name='media_url',
            field=models.CharField(blank=True, default='', max_length=2000),
        ),
        migrations.AlterField(
            model_name='source',
            name='url',
            field=models.CharField(blank=True, default='', max_length=2000),
        ),
    ]
