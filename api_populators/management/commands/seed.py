import contextlib
import json
import time
from concurrent import futures
from typing import Any, Dict, List, Optional

import requests
from difflib import SequenceMatcher
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db.utils import OperationalError
from langcodes import Language as Lang
from django.db.models import Q

from api.models import (AgeRating, AlternativeTitle, Collection, Cover, Game,
                        GameMode, GameVideo, Genre, Keyword, Language,
                        LanguageSupport, Website, LocaleCover, Multiplayer,
                        Platform, PlayerPerspective, ReleasePlatform, SupportType, LanguageTitle,
                        Theme, Thumbnail)
from api_populators.models import (Categories, PlatformType, Rating, RatingOrg,
                                   Regions, Status, Link)
from main import settings

data = 'fields *; limit 500;'
headers = {
    'Client-ID': settings.TWITCH_CLIENT_ID,
    'Authorization': f'Bearer {settings.TWITCH_AUTH}',
    'Accept': 'application/json'
}


def fetch_igdb_games(offset: int = 0, limit: int = 100, ids: Optional[List[int]] = None):
    """Fetch games from IGDB API

    Args:
        offset (int, optional): the offset used for extract multiple games. Defaults to 0.
        limit (int, optional): the limit the API has. Defaults to 100.
        ids (List[int], optional): the ids used to scrape instead of normal request. Defaults to None.

    Returns:
        List[Dict]: list of dictionaries of the fetched games
    """
    limit = f'limit {limit};'
    fields = [
        'name',
        'tags',
        'category',
        'first_release_date',
        'game_localizations.*',
        'game_localizations.cover.*',
        'game_localizations.region.*',
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
        'dlcs',
        'similar_games',
        'expanded_games',
        'standalone_expansions',
        'expansions',
        'remakes',
        'remasters',
        'language_supports.language.*',
        'language_supports.language_support_type.*',
        'game_modes.*',
        'multiplayer_modes.*',
        'multiplayer_modes.platform',
        'player_perspectives.*',
        'status',
        'storyline',
        'summary',
        'videos.*',
        'websites.*'
    ]
    joined_fields = f'fields {",".join(fields)};'
    url = 'https://api.igdb.com/v4/games'
    where = 'where id = ' + ' | id = '.join([str(id) for id in ids]) + \
        ';' if ids else ''
    response = requests.post(
        url,
        data=joined_fields+limit+f'offset {offset};{where}',
        headers=headers
    )
    data = response.json()
    print(f'{len(data)} games scraped successfully')

    return data


def clear_data():
    with contextlib.suppress(Exception):
        Game.objects.all().delete()


def populate_age_ratings():
    url = 'https://api.igdb.com/v4/age_ratings'
    response = requests.post(
        url,
        data=data,
        headers=headers
    )
    for age_rating in response.json():
        rating = Rating(int(age_rating['rating'])).label
        organization = AgeRating.Organizations(RatingOrg(int(age_rating['category'])).label)
        AgeRating.objects.get_or_create(
            rating=rating,
            organization=organization
        )


def populate_platforms():
    url = 'https://api.igdb.com/v4/platforms'
    response = requests.post(
        url,
        data=data,
        headers=headers
    )
    for platform in response.json():
        abbreviation = platform.get('abbreviation')
        alternative_name = platform.get('alternative_name')
        name = platform.get('name')
        platform_type = Platform.Type.UNDEFINED
        if platform.get('category'):
            platform_type = Platform.Type(PlatformType(int(platform['category'])).name)

        Platform.objects.get_or_create(name=name, type=platform_type, abbreviation=abbreviation,
                                       alternative_name=alternative_name)

    for support_type in SupportType.Enum.choices:
        SupportType.objects.get_or_create(name=support_type[1])


def populate_languages():
    url = 'https://api.igdb.com/v4/languages'
    response = requests.post(
        url,
        data=data,
        headers=headers
    )
    for language in response.json():
        Language.objects.get_or_create(
            locale=language['locale'],
            name=language['name'],
            native_name=language['native_name']
        )


def _populate_executor(igdb_games, model: Optional[Game | Collection] = None, attr: Optional[str] = None):
    """Thread Pool Executor used to populate database

    Args:
        igdb_games (List[Dict]): list of dictionaries that contains the games
        model (Game  |  Collection, optional): model used to add the saved game. Defaults to None.
        attr (Optional[str], optional): attribute where the model should add the game. Defaults to None.
    """
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        game_futures = [executor.submit(populate_game, game) for game in igdb_games]
        for future in futures.as_completed(game_futures):
            igdb_game: Game = future.result()
            if model and attr:
                getattr(model, attr).add(igdb_game)


def seed_model(json_data: Optional[List[Dict]] = None):
    """Function used to seed the database model"""
    igdb_games = json_data or []

    if not json_data:
        offset = 0
        total_igdb_games = 10000
        with futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_offset = {executor.submit(fetch_igdb_games, offset, min(
                total_igdb_games - offset, 500)): offset for offset in range(0, total_igdb_games, 500)}
            for future in futures.as_completed(future_to_offset):
                offset = future_to_offset[future]
                try:
                    games = future.result()
                    igdb_games.extend(games)
                except Exception as e:
                    print(f"Failed to fetch games starting from offset {offset}: {e}")

    _populate_executor(igdb_games)


def populate_game(game: Dict[str, Any]):
    """Function used to populate the game

    Args:
        game (Dict[str, Any]): dictionary of the game from the fetched data

    Returns:
        Game: Game model used to populate
    """
    try:
        game_type = Categories(int(game['category'])).label
    except Exception:
        print(game)
        exit()
    game_title = game.get('name')
    game_summary = game.get('summary')
    game_story_line = game.get('story_line')
    game_first_release = str(game['first_release_date']
                             ) if 'first_release_date' in game else None
    game_status = Status(int(game.get('status', 8))).label
    try:
        igdb_data, _ = Game.objects.update_or_create(
            title=game_title,
            cover=add_game_cover(game=game),
            defaults={
                'summary': game_summary,
                'story_line': game_story_line,
                'first_release': game_first_release,
                'type': Game.Type(game_type),
                'status': Game.Status(game_status),
            }
        )
    except OperationalError:
        time.sleep(5)
        return populate_game(game)

    _add_relations(game, igdb_data)

    return igdb_data


def _add_relations(game, igdb_data):
    """Private function to add relations in the database model

    Args:
        game (Dict): dictionary of the game that want to add to the database
        igdb_data (Game): model of the game that should be relationated
    """
    print(f'Populating with {game.get("name")}')
    # TODO: 
    add_language_support(igdb_data, game)
    # add_collections(game.get('collection'))
    add_videos(igdb_data, game.get('videos'))
    add_websites(igdb_data, game.get('websites'))
    add_related_data(igdb_data, game, Genre, "genres")
    add_related_data(igdb_data, game, Keyword, "keywords")
    add_related_data(igdb_data, game, Theme, "themes")
    add_age_ratings(igdb_data, game)
    add_release_platforms(igdb_data, game)
    add_player_perspective(igdb_data, game.get('player_perspectives', []))
    add_thumbnails(igdb_data, game.get('screenshots'))
    # add_parsed_games(igdb_data, game)


def add_release_platforms(igdb_data, game):
    """Add release dates to game model

    Args:
        igdb_data (Game): Game model to populate
        game (Dict[str, Any]): Dictionary of the game
    """
    multiplayer_modes = game.get('multiplayer_modes', [])
    all_multiplayer_platforms = []

    for mode in multiplayer_modes:
        platform = mode.get('platform', {})
        name = platform.get('name')
        all_multiplayer_platforms.append(name)

    for release_platform in game.get('release_dates', []):
        platform = release_platform.get('platform', {})
        platform_name = platform.get('name')

        platform_type = Platform.Type.UNDEFINED
        if platform.get('category'):
            platform_type = Platform.Type(PlatformType(int(platform['category'])).name)

        platform_obj = Platform.objects.get(name=platform_name, type=platform_type)

        region_label = Regions(int(release_platform['region'])).label

        valid_date = 'date' in release_platform
        release_date = str(release_platform['date']) if valid_date else None

        multiplayer_obj = add_multiplayer(all_multiplayer_platforms, platform_obj, multiplayer_modes)

        ReleasePlatform.objects.get_or_create(
            game=igdb_data,
            region=region_label,
            platform=platform_obj,
            multiplayer_modes=multiplayer_obj,
            defaults={'release_date': release_date}
        )

    multiplayer_keys = [element.keys() for element in multiplayer_modes]
    selected_modes = select_game_modes(multiplayer_keys)
    alternative_game_modes = {'name': mode for mode in selected_modes}
    add_related_data(igdb_data, game, GameMode, 'game_modes')
    add_related_data(igdb_data, alternative_game_modes, GameMode, 'game_modes')


def select_game_modes(game_modes: List[str]) -> List[str]:
    available_modes = {
        'campaigncoop': ['Co-Operative'],
        'dropin': ['Co-Operative'],
        'lancoop': ['Co-Operative', 'Multiplayer'],
        'offlinecoop': ['Co-Operative', 'Single player'],
        'onlinecoop': ['Co-Operative', 'Multiplayer'],
        'splitscreen': ['Split screen'],
        'splitscreenonline': ['Split screen', 'Multiplayer']
    }

    selected_modes = set()
    for mode, modes in available_modes.items():
        if mode in game_modes:
            selected_modes.update(modes)

    return list(selected_modes)


def add_multiplayer(all_multiplayer_platforms: List, platform_obj, multiplayer_modes: List):
    try:
        index = all_multiplayer_platforms.index(platform_obj.name)

        multiplayer_mode = multiplayer_modes[index]
        multiplayer_obj, _ = Multiplayer.objects.get_or_create(
            campaign_coop=multiplayer_mode.get("campaigncoop"),
            drop_in=multiplayer_mode.get("dropin"),
            lan_coop=multiplayer_mode.get("lancoop"),
            offline_coop=multiplayer_mode.get("offlinecoop"),
            offline_coop_players=multiplayer_mode.get("offlinecoopmax"),
            offline_players=multiplayer_mode.get("offlinemax"),
            online_coop=multiplayer_mode.get("onlinecoop"),
            online_coop_players=multiplayer_mode.get("onlinecoopmax"),
            online_players=multiplayer_mode.get("onlinemax"),
            splitscreen=multiplayer_mode.get("splitscreen"),
            splitscreen_online=multiplayer_mode.get("splitscreenonline")
        )
    except ValueError:
        multiplayer_obj = None

    return multiplayer_obj


def add_player_perspective(igdb_data: Game, player_perspectives: List):
    for player_perspective in player_perspectives:
        perspective_obj, _ = PlayerPerspective.objects.get_or_create(
            name=player_perspective['name'],
        )
        igdb_data.player_perspectives.add(perspective_obj)


def add_videos(igdb_data: Game, videos: Optional[List[Dict]]):
    """Add videos to game model

    Args:
        igdb_data (Game): Game model to populate
        videos (Optional[List[Dict]]): List of dictionaries that contains the videos
    """
    if not videos:
        return

    for video in videos:
        GameVideo.objects.get_or_create(
            type=video.get('name', 'Trailer'),
            game=igdb_data,
            video_id=video.get('video_id')
        )


def add_thumbnails(igdb_data: Game, thumbnails: Optional[List[Dict]]):
    """Add thumbnails to game model

    Args:
        igdb_data (Game): Game model to populate
        thumbnails (Optional[List[Dict]]): List of dictionaries that contains the thumbnail images
    """
    if not thumbnails:
        return

    game_title: str = igdb_data.title
    for i, thumbnail in enumerate(thumbnails):
        thumbnail_obj, thumbnail_created = Thumbnail.objects.get_or_create(
            filename=slugify(f'{game_title}--{i}'),
            game=igdb_data,
            defaults={
                'url': thumbnail.get('url'),
                'animated': thumbnail.get('animated')
            }
        )

        if thumbnail_created:
            thumbnail_obj.save()


def add_websites(igdb_data: Game, links: Optional[List[Dict]]):
    """Add website links to game model

    Args:
        igdb_data (Game): Game model to populate
        links (Optional[List[Dict]]): List of dictionaries that contains the links
    """
    if not links:
        return

    for link in links:
        link_category = Link(int(link.get('category'))).label
        link_obj, link_created = Website.objects.get_or_create(
            category=Website.Link(link_category),
            game=igdb_data,
            trusted=link.get('trusted'),
            url=link.get('url')
        )


def add_collections(collection: Optional[Dict[str, Any]]):
    """Add collection to game model

    Args:
        collection (Optional[Dict[str, Any]]): List of dictionaries that contains the collection data
    """
    if collection:
        collection_name = collection.get('name')
        collection_obj, collection_created = Collection.objects.get_or_create(
            name=collection_name
        )
        if collection_created:
            collection_obj.save()
        data = fetch_igdb_games(limit=len(collection.get('games')), ids=collection.get('games'))
        _populate_executor(data, collection_obj, 'games')


def add_parsed_games(igdb_data: Game, game: Dict[str, Any]):
    """Add parsed games (DLCs, Similars, Expanded, Expansions, Remakes, Remasters) to game model

    Args:
        igdb_data (Game): Game model to populate
        game (Dict[str, Any]): Dictionary of the game
    """
    if game.get('dlcs'):
        data = fetch_igdb_games(limit=len(game.get('dlcs')), ids=game.get('dlcs'))
        _populate_executor(data, igdb_data, 'dlcs')
    if game.get('similar_games'):
        data = fetch_igdb_games(limit=len(game.get('similar_games')), ids=game.get('similar_games'))
        _populate_executor(data, igdb_data, 'similar_games')
    if game.get('expanded_games'):
        data = fetch_igdb_games(limit=len(game.get('expanded_games')), ids=game.get('expanded_games'))
        _populate_executor(data, igdb_data, 'expanded_games')
    if game.get('standalone_expansions'):
        data = fetch_igdb_games(limit=len(game.get('standalone_expansions')), ids=game.get('standalone_expansions'))
        _populate_executor(data, igdb_data, 'standalone_expansions')
    if game.get('expansions'):
        data = fetch_igdb_games(limit=len(game.get('expansions')), ids=game.get('expansions'))
        _populate_executor(data, igdb_data, 'expansions')
    if game.get('remakes'):
        data = fetch_igdb_games(limit=len(game.get('remakes')), ids=game.get('remakes'))
        _populate_executor(data, igdb_data, 'remakes')
    if game.get('remasters'):
        data = fetch_igdb_games(limit=len(game.get('remasters')), ids=game.get('remasters'))
        _populate_executor(data, igdb_data, 'remasters')


def add_language_support(igdb_data: Game, game: Dict[str, Any]):
    """Add language supports to game model

    Args:
        igdb_data (Game): Game model to populate
        game (Dict[str, Any]): Dictionary of the game
    """
    language_supports = game.get('language_supports', [])
    alt_titles: List = game.get('alternative_names', [])
    localizations = game.get('game_localizations', [])

    all_names = [el.get('name').lower() for el in alt_titles]

    for localization in localizations:
        name = localization.get('name')
        if not name:
            alt_titles.append(localization)
            continue

        if matches := [
            (index, SequenceMatcher(None, alt_name.strip(), name.strip()).ratio())
            for index, alt_name in enumerate(all_names)
        ]:
            index, sim = max(matches, key=lambda x: x[1])
            if sim > 0.8:
                alt_titles[index].update(localization)
                continue

        alt_titles.append(localization)

    for language_support in language_supports:
        language: Dict = language_support.get('language')
        lang_code = language.get('locale')

        language_obj = Language.objects.get(locale=lang_code)

        support: Dict = language_support.get('language_support_type')
        support_name = SupportType.Enum(support['name'])
        support_obj = SupportType.objects.get(name=support_name)

        lang_supports_obj, _ = LanguageSupport.objects.get_or_create(
            game=igdb_data,
            language=language_obj,
            defaults={'cover': None}
        )
        lang_supports_obj.support_types.add(support_obj)

    for alt_title in alt_titles:
        alt_name = alt_title.get('name')
        alt_comment = alt_title.get('comment', 'Others')
        alt_language = alt_comment.split()[0]
        cover_obj = None
        try:
            lang_code = alt_title.get('region', {'identifier': None})['identifier'] or Lang.find(alt_language)
            language_obj = Language.objects.filter(Q(name__trigram_similar=alt_comment.replace(
                'title', '').strip()) | Q(locale__startswith=lang_code))[0]

            if 'cover' in alt_title:
                cover = alt_title['cover']
                cover_obj = LocaleCover.objects.create(
                    filename=slugify(f'{igdb_data.title}-{language_obj.locale}'),
                    url=cover['url'],
                    animated=cover['animated']
                )
            lang_supports_obj, _ = LanguageSupport.objects.update_or_create(
                game=igdb_data,
                language=language_obj,
                defaults={'cover': cover_obj}
            )

            if alt_name:
                LanguageTitle.objects.create(
                    title=alt_name,
                    description=alt_comment,
                    language_support=lang_supports_obj
                )

        except LookupError:
            AlternativeTitle.objects.create(
                title=alt_name,
                type=alt_comment,
                game=igdb_data
            )

    # print(json.dumps(language_supports, indent=4))


def add_game_cover(game: Dict) -> Cover:
    """Add game's cover to game model

    Args:
        game(dict): Dictionary of the game

    Returns:
        Cover: _description_
    """
    game_title = game.get('name')
    if game.get('cover'):
        game_cover, game_cover_created = Cover.objects.get_or_create(
            filename=slugify(game_title),
            defaults={
                'url': game.get('cover').get('url'),
                'animated': game.get('cover', {}).get('animated')
            }
        )
    else:
        game_cover = None

    return game_cover


def add_related_data(igdb_data, obj, related_model, related_data):
    """Add related data to game model

    Args:
        igdb_data(Model): Model to populate
        obj(Dict[str, Any]): Dictionary of the object
        related_model(ModelType): ModelType related to Game model used to get or create the object
        related_data(str): Attribute that should be contained in Game model
    """
    for related_object in obj.get(related_data, []):
        related_slug = slugify(related_object['name'])
        with contextlib.suppress(Exception):
            related_obj, _ = related_model.objects.get_or_create(
                name=related_object['name'],
                url=f'http://127.0.0.1:8000/{related_data.replace("_", "-")}/{related_slug}',
                defaults={'slug': related_slug},
            )
        getattr(igdb_data, related_data).add(related_obj)


def add_age_ratings(igdb_data, game):
    """Add age ratings to game model

    Args:
        igdb_data(Game): Game model to populate
        game(Dict[str, Any]): Dictionary of the game
    """
    for age_rating in game.get('age_ratings', []):
        rating = Rating(int(age_rating['rating'])).label
        organization = AgeRating.Organizations(RatingOrg(int(age_rating['category'])).label)
        age_rating_obj, _ = AgeRating.objects.get_or_create(
            rating=rating,
            organization=organization
        )

        igdb_data.age_ratings.add(age_rating_obj)


class Command(BaseCommand):
    """Command handled by Django

    Args:
        BaseCommand(Type): Parent of the class
    """

    def handle(self, *args, **options):
        """Function to handle the seed_model"""
        # clear_data()
        populate_age_ratings()
        populate_languages()
        populate_platforms()
        with open('exs.json', encoding="utf8") as json_file:
            data = json.load(json_file)
            seed_model()
        # clear_data()
        print("IGDB API was successfully added")
