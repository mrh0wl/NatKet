# Generated by Django 4.1.7 on 2023-03-09 21:30

import api.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_languagesupport_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='releaseplatform',
            name='release_date',
            field=api.fields.UCDateTimeField(blank=True, null=True),
        ),
    ]