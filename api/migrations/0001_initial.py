# Generated by Django 4.0.3 on 2022-04-02 21:01

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0004_alter_taggeditem_content_type_alter_taggeditem_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interface', models.CharField(choices=[('twitter', 'Twitter'), ('website', 'Website'), ('api', 'API')], max_length=50)),
                ('source', models.CharField(max_length=250)),
                ('headline', models.CharField(blank=True, max_length=250)),
                ('text', models.TextField()),
                ('language', models.CharField(choices=[('en', 'English'), ('ru', 'Russian'), ('ua', 'Ukrainian')], max_length=2)),
                ('pinned', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('en', 'English'), ('ru', 'Russian'), ('ua', 'Ukrainian')], max_length=2)),
                ('text', models.TextField()),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.source')),
            ],
        ),
    ]