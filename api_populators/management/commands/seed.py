import contextlib
from concurrent import futures

import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from api.models import (AgeRating, Game, Genre, Keyword,
                        Platform, ReleaseDate, Theme, Cover)
from api_populators.models import (Categories, PlatformType, Rating, RatingOrg,
                                   Regions, Status)
from main import settings


def fetch_igdb_games(offset: int, limit: int):
    limit = f'limit {limit};'
    headers = {
        'Client-ID': settings.TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {settings.TWITCH_AUTH}',
        'Accept': 'application/json'
    }
    fields = [
        'name',
        'tags',
        'category',
        'first_release_date',
        'genres.*',
        'keywords.*',
        'themes.*',
        'release_dates.*',
        'release_dates.platform.*',
        'release_dates.platform.versions.*',
        'release_dates.platform.platform_logo.*',
        'release_dates.platform.websites.*',
        'age_ratings.*',
        'screenshots.*',
        'collection.*',
        'alternative_names.*',
        'cover.*',
        'dlcs.*',
        'expanded_games.*',
        'expansions.*',
        'language_supports.*',
        'game_modes.*',
        'multiplayer_modes.*',
        'status',
        'storyline',
        'summary',
        'videos.*',
        'websites.*'
    ]
    joined_fields = f'fields {",".join(fields)};'
    url = 'https://api.igdb.com/v4/games'
    response = requests.post(
        url,
        data=joined_fields+limit+f'offset {offset}; where status = 0;',
        headers=headers
    )
    data = response.json()
    print(f'{len(data)} games scraped successfully')

    return data


def clear_data():
    with contextlib.suppress(Exception):
        Game.objects.all().delete()


def seed_model():
    offset = 0
    total_igdb_games = 40  # 222000
    igdb_games = []

    with futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_offset = {executor.submit(fetch_igdb_games, offset, min(
            total_igdb_games - offset, 500)): offset for offset in range(0, total_igdb_games, 500)}
        for future in futures.as_completed(future_to_offset):
            offset = future_to_offset[future]
            try:
                games = future.result()
                igdb_games.extend(games)
            except Exception as e:
                print(
                    f"Failed to fetch games starting from offset {offset}: {e}")

    for game in igdb_games:
        game_type = Categories(int(game['category'])).label
        game_title = game.get('name')
        game_summary = game.get('summary', None)
        game_story_line = game.get('story_line', None)
        game_first_release = str(game['first_release_date']
                                 ) if 'first_release_date' in game else None
        game_cover = Cover(
            height=game['cover']['height'],
            width=game['cover']['width']
        ).get_image_from_url(url=game.get('cover').get('url'), filename=slugify(game_title))
        game_cover.save()
        game_status = Status(int(game.get('status', 8))).label
        igdb_data = Game.objects.create(
            title=game_title,
            cover=game_cover,
            summary=game_summary,
            story_line=game_story_line,
            first_release=game_first_release,
            type=Game.Type(game_type),
            status=Game.Status(game_status),
        )

        add_game_related_data(igdb_data, game, Genre, "genres")
        add_game_related_data(igdb_data, game, Keyword, "keywords")
        add_game_related_data(igdb_data, game, Theme, "themes")
        add_age_ratings(igdb_data, game)
        add_release_dates(igdb_data, game)
        igdb_data.save()


def add_game_related_data(igdb_data, game, related_model, related_data):
    for related_object in game.get(related_data, []):
        related_slug = slugify(related_object['name'])
        with contextlib.suppress(Exception):
            related_obj, related_created = related_model.objects.get_or_create(
                name=related_object['name'],
                url=f'http://127.0.0.1:8000/{related_data}/{related_slug}',
                defaults={'slug': related_slug},
            )
        if related_created:
            related_obj.save()
        getattr(igdb_data, related_data).add(related_obj)


def add_age_ratings(igdb_data, game):
    for age_rating in game.get('age_ratings', []):
        rating = Rating(int(age_rating['rating'])).label
        organization = AgeRating.Organizations(RatingOrg(int(age_rating['category'])).label)
        age_rating_obj, age_rating_created = AgeRating.objects.get_or_create(
            rating=rating,
            organization=organization
        )
        if age_rating_created:
            age_rating_obj.save()

        igdb_data.age_ratings.add(age_rating_obj)


def add_release_dates(igdb_data, game):
    for release_date in game.get('release_dates', []):
        platform = release_date['platform']
        abbreviation = platform.get('abbreviation')
        alternative_name = platform.get('alternative_name')
        name = platform.get('name')

        platform_type = Platform.Type.UNDEFINED
        if 'category' in platform:
            platform_type = Platform.Type(
                PlatformType(int(platform['category'])).name
            )
        elif name.upper() in PlatformType.names:
            platform_type = Platform.Type(name.upper())

        platform_obj, platform_created = Platform.objects.get_or_create(
            name=name,
            abbreviation=abbreviation,
            alternative_name=alternative_name,
            type=platform_type
        )
        if platform_created:
            platform_obj.save()
        valid_date = 'date' in release_date
        release_date_obj = ReleaseDate.objects.create(
            date=str(release_date['date']) if valid_date else None,
            region=ReleaseDate.Regions(
                Regions(
                    int(release_date['region'])
                ).label
            ),
            platform=platform_obj
        )
        # release_date_obj.platform.add(platform_obj)
        igdb_data.release_dates.add(release_date_obj)


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_data()
        seed_model()
        # clear_data()
        print("IGDB API was successfully added")
