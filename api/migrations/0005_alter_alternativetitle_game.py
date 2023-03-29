# Generated by Django 4.1.7 on 2023-03-15 07:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_alternativetitle_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alternativetitle',
            name='game',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='alternative_titles', to='api.game'),
        ),
    ]
