# Generated by Django 4.1.7 on 2023-03-04 08:24

import api.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AgeRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('rating', models.CharField(max_length=8)),
                ('organization', models.CharField(choices=[('ESRB', 'ESRB'), ('PEGI', 'PEGI'), ('CERO', 'CERO'), ('USK', 'USK'), ('GRAC', 'GRAC'), ('CLASSIND', 'CLASSIND'), ('ACB', 'ACB')], default='ESRB', max_length=8)),
            ],
            options={
                'ordering': ['-organization'],
            },
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100)),
                ('summary', models.CharField(blank=True, default=None, max_length=5000, null=True)),
                ('story_line', models.CharField(blank=True, default=None, max_length=5000, null=True)),
                ('slug', models.SlugField(allow_unicode=True, max_length=255, unique=True, verbose_name='slug')),
                ('first_release', api.fields.UCDateTimeField(null=True)),
                ('type', models.CharField(choices=[('MG', 'Main Game'), ('DLC', 'DLC Addon'), ('EXP', 'Expansion'), ('BD', 'Bundle'), ('SEXP', 'Standalone Expansion'), ('MOD', 'Mod'), ('EP', 'Episode'), ('S', 'Season'), ('RM', 'Remake'), ('RMA', 'Remaster'), ('EG', 'Expanded Game'), ('P', 'Port'), ('F', 'Fork'), ('PCK', 'Pack'), ('U', 'Update')], max_length=4)),
                ('status', models.CharField(choices=[('F', 'Released'), ('A', 'Alpha'), ('B', 'Beta'), ('E', 'Early'), ('O', 'Offline'), ('C', 'Cancelled'), ('R', 'Rumored'), ('D', 'Delisted')], max_length=4)),
                ('age_ratings', models.ManyToManyField(to='api.agerating')),
                ('dlcs', models.ManyToManyField(to='api.game')),
                ('expanded_games', models.ManyToManyField(to='api.game')),
                ('expansions', models.ManyToManyField(to='api.game')),
            ],
            options={
                'verbose_name': 'Game',
                'verbose_name_plural': 'Games',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='GameMode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('name', models.TextField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('url', models.URLField(max_length=250)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('name', models.TextField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('url', models.URLField(max_length=250)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImageBase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('animated', models.BooleanField(default=False, null=True)),
                ('height', models.PositiveIntegerField(blank=True, null=True)),
                ('width', models.PositiveIntegerField(blank=True, null=True)),
                ('filename', models.SlugField(blank=True, max_length=100, null=True)),
                ('url', models.URLField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('name', models.TextField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('url', models.URLField(max_length=250)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('locale', models.CharField(max_length=10, null=True)),
                ('name', models.CharField(max_length=100, null=True)),
                ('native_name', models.CharField(max_length=100, null=True)),
            ],
            options={
                'ordering': ['locale'],
            },
        ),
        migrations.CreateModel(
            name='Multiplayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('campaign_coop', models.BooleanField(default=False)),
                ('drop_in', models.BooleanField(default=False)),
                ('lan_coop', models.BooleanField(default=False)),
                ('offline_coop', models.BooleanField(default=False)),
                ('offline_coop_players', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('offline_players', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('online_coop', models.BooleanField(default=False)),
                ('online_coop_players', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('online_players', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('splitscreen', models.BooleanField(default=False)),
                ('splitscreen_online', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ObjectWithImageField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='static/{}')),
                ('image_url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('abbreviation', models.CharField(max_length=20, null=True)),
                ('alternative_name', models.CharField(max_length=100, null=True)),
                ('type', models.CharField(choices=[('CONSOLE', 'Console'), ('ARCADE', 'Arcade'), ('PLATFORM', 'Platform'), ('OPERATING_SYSTEM', 'Operating System'), ('PORTABLE_CONSOLE', 'Portable Console'), ('COMPUTER', 'Computer'), ('UNDEFINED', 'Undefined')], max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlayerPerspective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('name', models.TextField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('url', models.URLField(max_length=250)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('locale', models.CharField(max_length=10)),
                ('name', models.CharField(default='en-us', max_length=70)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SupportType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=30, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('type_id', models.PositiveIntegerField(choices=[(0, 'Theme'), (1, 'Genre'), (2, 'Keyword'), (3, 'Game')])),
                ('endpoint_id', models.PositiveIntegerField()),
                ('value', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
                'ordering': ['value'],
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('name', models.TextField(max_length=200)),
                ('slug', models.SlugField(unique=True)),
                ('url', models.URLField(max_length=250)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=400)),
                ('github_id', models.BigIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cover',
            fields=[
                ('imagebase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.imagebase')),
            ],
            options={
                'abstract': False,
            },
            bases=('api.imagebase',),
        ),
        migrations.CreateModel(
            name='LocaleCover',
            fields=[
                ('imagebase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.imagebase')),
            ],
            options={
                'abstract': False,
            },
            bases=('api.imagebase',),
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('category', models.CharField(choices=[('Official', 'Official Website'), ('Wikia', 'Fandom Wiki'), ('Wikipedia', 'Wikipedia'), ('Facebook', 'Facebook'), ('Twitter', 'Twitter'), ('Twitch', 'Twitch'), ('Instagram', 'Instagram'), ('Youtube', 'Youtube'), ('Iphone', 'App Store (iPhone)'), ('Ipad', 'App Store (iPad)'), ('Android', 'Google Play'), ('Steam', 'Steam'), ('Reddit', 'Subreddit'), ('Itch', 'Itch.io'), ('Epicgames', 'Epic Games'), ('Gog', 'GoG'), ('Discord', 'Official Discord')], max_length=100)),
                ('trusted', models.BooleanField(default=False)),
                ('url', models.URLField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='websites', to='api.game')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('github_id', models.BigIntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.user')),
            ],
        ),
        migrations.CreateModel(
            name='ReleasePlatform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('release_date', api.fields.UCDateTimeField()),
                ('region', models.CharField(choices=[('EU', 'Europe'), ('ES', 'Spanish'), ('LAT', 'Spanish (LATAM)'), ('NA', 'North America'), ('AU', 'Australia'), ('NZ', 'New Zealand'), ('JP', 'Japan'), ('CH', 'China'), ('AS', 'Asia'), ('WW', 'Worldwide'), ('KR', 'Korea'), ('BR', 'Brazil')], max_length=3)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='release_platforms', to='api.game')),
                ('multiplayer_modes', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.multiplayer')),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.platform')),
            ],
        ),
        migrations.CreateModel(
            name='GameVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('type', models.CharField(max_length=100)),
                ('video_id', models.CharField(max_length=50)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='api.game')),
            ],
            options={
                'ordering': ['type'],
            },
        ),
        migrations.AddField(
            model_name='game',
            name='game_modes',
            field=models.ManyToManyField(to='api.gamemode'),
        ),
        migrations.AddField(
            model_name='game',
            name='genres',
            field=models.ManyToManyField(to='api.genre'),
        ),
        migrations.AddField(
            model_name='game',
            name='keywords',
            field=models.ManyToManyField(to='api.keyword'),
        ),
        migrations.AddField(
            model_name='game',
            name='player_perspectives',
            field=models.ManyToManyField(to='api.playerperspective'),
        ),
        migrations.AddField(
            model_name='game',
            name='remakes',
            field=models.ManyToManyField(to='api.game'),
        ),
        migrations.AddField(
            model_name='game',
            name='remasters',
            field=models.ManyToManyField(to='api.game'),
        ),
        migrations.AddField(
            model_name='game',
            name='similar_games',
            field=models.ManyToManyField(to='api.game'),
        ),
        migrations.AddField(
            model_name='game',
            name='standalone_expansions',
            field=models.ManyToManyField(to='api.game'),
        ),
        migrations.AddField(
            model_name='game',
            name='tags',
            field=models.ManyToManyField(to='api.tag'),
        ),
        migrations.AddField(
            model_name='game',
            name='themes',
            field=models.ManyToManyField(to='api.theme'),
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=150)),
                ('slug', models.SlugField(unique=True)),
                ('url', models.URLField(max_length=250)),
                ('games', models.ManyToManyField(related_name='collection', to='api.game')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AlternativeTitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=100)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alternative_titles', to='api.game')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('imagebase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='api.imagebase')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='thumbnails', to='api.game')),
            ],
            options={
                'abstract': False,
            },
            bases=('api.imagebase',),
        ),
        migrations.CreateModel(
            name='LanguageSupport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', api.fields.UCDateTimeField(auto_now_add=True)),
                ('updated_at', api.fields.UCDateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=100, null=True)),
                ('description', models.CharField(max_length=100, null=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='language_supports', to='api.game')),
                ('language', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.language')),
                ('support_types', models.ManyToManyField(to='api.supporttype')),
                ('cover', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.localecover')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='game',
            name='cover',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.cover'),
        ),
    ]
