# Generated by Django 4.1.7 on 2023-03-15 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_releaseplatform_release_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alternativetitle',
            name='title',
            field=models.CharField(max_length=250),
        ),
    ]
