# Generated by Django 2.0.6 on 2018-06-05 14:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extractor', '0003_extracteddata'),
    ]

    operations = [
        migrations.RenameField(
            model_name='extracteddata',
            old_name='filename',
            new_name='file',
        ),
        migrations.RenameField(
            model_name='pdf',
            old_name='filename',
            new_name='file',
        ),
    ]