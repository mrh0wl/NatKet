# Generated by Django 4.1.7 on 2023-03-04 11:53

import api.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='languagesupport',
            name='description',
        ),
        migrations.RemoveField(
            model_name='languagesupport',
            name='title',
        ),
        migrations.CreateModel(
            name='LanguageTitles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100, null=True)),
                ('description', models.CharField(max_length=100, null=True)),
                ('language_support', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='language_titles', to='api.languagesupport')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
