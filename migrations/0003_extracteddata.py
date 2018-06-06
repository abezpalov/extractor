# Generated by Django 2.0.6 on 2018-06-05 13:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('extractor', '0002_auto_20180605_1247'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtractedData',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, default=None, max_length=256, null=True)),
                ('filename', models.FileField(blank=True, default=None, max_length=1024, null=True, upload_to='')),
                ('pdf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='extractor.PDF')),
            ],
        ),
    ]
