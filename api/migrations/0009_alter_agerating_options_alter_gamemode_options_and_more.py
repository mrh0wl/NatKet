# Generated by Django 4.1.7 on 2023-03-27 22:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_website_url'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agerating',
            options={'ordering': ['rating']},
        ),
        migrations.AlterModelOptions(
            name='gamemode',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='keyword',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='platform',
            options={'ordering': ['name'], 'verbose_name': 'Platform', 'verbose_name_plural': 'Platforms'},
        ),
        migrations.AlterModelOptions(
            name='playerperspective',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='theme',
            options={'ordering': ['name']},
        ),
    ]
