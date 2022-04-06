# Generated by Django 4.0.3 on 2022-04-06 03:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('point', models.CharField(blank=True, max_length=100)),
                ('bounding_box', models.TextField(blank=True)),
            ],
        ),
        migrations.AlterField(
            model_name='translation',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='api.source'),
        ),
        migrations.AddIndex(
            model_name='source',
            index=models.Index(fields=['timestamp'], name='timestamp_idx'),
        ),
        migrations.AddField(
            model_name='location',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='api.source'),
        ),
        migrations.AddIndex(
            model_name='location',
            index=models.Index(fields=['name'], name='name_idx'),
        ),
    ]
