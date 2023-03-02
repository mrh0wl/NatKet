import contextlib
import time
import json
from concurrent import futures
from typing import Any, Dict, List, Optional
from langcodes import Language as Lang

import requests
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from api.models import (AgeRating, Collection, Cover, Game,
                        GameModes, GameVideo, Genre, Keyword, Language,
                        LanguageSupport, Links, LocaleCover, Multiplayer,
                        Platform, PlayerPerspective, ReleaseDate, SupportType, AlternativeTitle,
                        Theme, Thumbnail)
from api_populators.models import (Categories, PlatformType, Rating, RatingOrg,
                                   Regions, Status, Websites)
from main import settings


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
        'status',
        'storyline',
        'summary',
        'videos.*',
        'websites.*'
    ]
    joined_fields = f'fields {",".join(fields)};'
    url = 'https://api.igdb.com/v4/games'
    where = 'where id = ' + ' | id = '.join([str(id) for id in ids]) + \
        ';' if ids else 'sort first_release_date desc; where game_localizations.cover != null & name ~ "Aokana"*;'
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
            igdb_game.save()
            if model and attr:
                getattr(model, attr).add(igdb_game)


def seed_model(json_data: Optional[List[Dict]] = None):
    """Function used to seed the database model"""
    igdb_games = json_data or []

    if not json_data:
        offset = 0
        total_igdb_games = 1
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
    igdb_data, igdb_data_created = Game.objects.get_or_create(
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
    _add_relations(game, igdb_data)

    # time.sleep(10)
    return igdb_data


def _add_relations(game, igdb_data):
    """Private function to add relations in the database model

    Args:
        game (Dict): dictionary of the game that want to add to the database
        igdb_data (Game): model of the game that should be relationated
    """
    print(f'Populating with {game.get("name")}')
    # add_alternative_names(igdb_data, alt_titles=)
    add_language_support(igdb_data, game)
    """ add_collections(game.get('collection'))
    add_videos(igdb_data, game.get('videos'))
    add_links(igdb_data, game.get('videos'))
    add_game_related_data(igdb_data, game, Genre, "genres")
    add_game_related_data(igdb_data, game, Keyword, "keywords")
    add_game_related_data(igdb_data, game, Theme, "themes")
    add_age_ratings(igdb_data, game)
    add_release_dates(igdb_data, game)
    add_thumbnails(igdb_data, game.get('screenshots'))
    add_parsed_games(igdb_data, game) """

    # TODO: Fix the game_modes population
    if not game.get('game_modes') and game.get('multiplayer_modes'):
        availables_modes = {
            'campaigncoop':  'Co-Operative',
            'dropin':  'Co-Operative',
            'lancoop':  ['Co-Operative', 'Multiplayer'],
            'offlinecoop':  ['Co-Operative', 'Single player'],
            'onlinecoop':  ['Co-Operative', 'Multiplayer'],
            'splitscreen':  'Split screen',
            'splitscreenonline':  ['Split screen', 'Multiplayer']
        }
        selected_modes = []
        if not any(
            game['multiplayer_modes'].get(key) for key in availables_modes
        ):
            selected_modes.append('Single player')
        else:
            for key, mode in availables_modes.items():
                if game['multiplayer_modes'].get(key) and mode not in selected_modes:
                    in_selected = set(selected_modes)
                    if isinstance(mode, list):
                        in_mode = set(mode)
                        duplicate_remover = in_mode - in_selected
                        selected_modes.extend(duplicate_remover)
                    else:
                        selected_modes.append(mode)
        for mode_name in selected_modes:
            add_game_modes(igdb_data, game, mode_name)
    else:
        for mode in game['game_modes']:
            add_game_modes(igdb_data, game, mode.get('name'))


def add_videos(igdb_data: Game, videos: Optional[List[Dict]]):
    """Add videos to game model

    Args:
        igdb_data (Game): Game model to populate
        videos (Optional[List[Dict]]): List of dictionaries that contains the videos
    """
    if not videos:
        return

    for video in videos:
        video_obj, video_created = GameVideo.objects.get_or_create(
            type=video.get('name'),
            game=igdb_data,
            video_id=video.get('video_id')
        )

        if video_created:
            video_obj.save()


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
                'animated': thumbnail.get('animated'),
                'height': thumbnail.get('height'),
                'width': thumbnail.get('width')
            }
        )

        if thumbnail_created:
            thumbnail_obj.save()


def add_links(igdb_data: Game, links: Optional[List[Dict]]):
    """Add website links to game model

    Args:
        igdb_data (Game): Game model to populate
        links (Optional[List[Dict]]): List of dictionaries that contains the links
    """
    if not links:
        return

    for link in links:
        link_category = Websites(int(link.get('category'))).label
        link_obj, link_created = Links.objects.get_or_create(
            category=link_category,
            game=igdb_data,
            trusted=link.get('trusted'),
            url=link.get('url')
        )

        if link_created:
            link_obj.save()


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


def add_game_modes(igdb_data: Game, game: Dict, mode_name: str):
    """Add game modes to game model

    Args:
        igdb_data (Game): Game model to populate
        game (Dict): Dictionary of the game to extract the data
        mode_name (str): Mode's name that should be added
    """
    mode_slug = slugify(mode_name)
    with contextlib.suppress(Exception):
        mode_obj, mode_created = GameModes.objects.get_or_create(
            name=mode_name,
            url=f'http://127.0.0.1:8000/game-modes/{mode_slug}',
            defaults={'slug': mode_slug},
        )
    if mode_created:
        if game.get('multiplayer_modes'):
            multiplayer_obj, multiplayer_created = Multiplayer.objects.get_or_create(
                campaign_coop=game['multiplayer_modes'].get('campaigncoop'),
                drop_in=game['multiplayer_modes'].get('dropin'),
                lan_coop=game['multiplayer_modes'].get('lancoop'),
                offline_coop=game['multiplayer_modes'].get('offlinecoop'),
                online_coop=game['multiplayer_modes'].get('onlinecoop'),
                splitscreen=game['multiplayer_modes'].get('splitscreen'),
                spliscreen_online=game['multiplayer_modes'].get('splitscreenonline')
            )
            if multiplayer_created:
                multiplayer_obj.save()
            mode_obj.multiplayer.add(multiplayer_obj)
        if game.get('player_perspectives'):
            pp_name = game['player_perspectives'].get('name')
            pp_slug = slugify(pp_name)
            pp_obj, pp_created = PlayerPerspective.objects.get_or_create(
                name=pp_name,
                url=f'http://127.0.0.1:8000/player-perspectives/{pp_slug}',
                defaults={'slug': pp_slug}
            )
            if pp_created:
                pp_obj.save()
            mode_obj.player_perspectives.add(pp_obj)
        mode_obj.save()
    igdb_data.game_modes.add(mode_obj)


def add_language_support(igdb_data: Game, game: Dict[str, Any]):
    """Add language supports to game model

    Args:
        igdb_data (Game): Game model to populate
        language_supports (List[Dict[str, Any]]): List of dictionaries that contains the supported languages
    """
    # TODO: add [] as default: game.get('key', [])
    language_supports = game.get('language_supports', [])
    alt_titles: List = game.get('alternative_names', [])
    localizations = game.get('game_localizations', [])

    all_names = [el.get('name').lower() for el in alt_titles]
    all_locales = [el.get('language', {}).get('locale') for el in language_supports]

    # TODO: if error getting language (Lang.find(language).language) -> create alternative_title
    for localization in localizations:
        try:
            index = all_names.index(localization.get('name').lower())
            alt_titles[index] = localization
        except ValueError:
            alt_titles.append(localization)

    for alt_title in alt_titles:

        if comment := alt_title.get('comment'):
            language = comment.split()[0]
        try:
            # if language.capitalize() not in ['Spanish', 'English']:
            lang_code = Lang.find(language).language

            req = requests.get(f'https://restcountries.com/v3.1/lang/{language}')
            res = req.json()
            country_code = res[0]
            code = f'{lang_code}-{country_code}'
            try:
                index = all_locales.index(alt_title.get('region', {}).get('identifier', code))
                # print(language_supports[index])

                language: Dict = language_supports[index].get('language')
                language_obj, _ = Language.objects.get_or_create(
                    locale=language.get('locale'),
                    defaults={
                        'name': language.get('name'),
                        'native_name': language.get('native_name')
                    }
                )

                support: Dict = language_supports.pop(index).get('language_support_type')
                all_locales.pop(index)
                support_obj, _ = SupportType.objects.get_or_create(
                    name=support.get('name')
                )

                if alt_title.get('cover'):
                    cover_obj, _ = LocaleCover.objects.get_or_create(
                        filename=slugify(f'{igdb_data.title}-{language_obj.locale}'),
                        defaults={
                            'url': alt_title.get('cover').get('url'),
                            'animated': alt_title.get('cover', {}).get('animated'),
                            'height': alt_title.get('cover', {}).get('height'),
                            'width': alt_title.get('cover', {}).get('width')
                        }
                    )
            except ValueError:
                language_obj = None
                support_obj = None
                cover_obj = None

            lang_supports_obj, _ = LanguageSupport.objects.update_or_create(
                game=igdb_data,
                defaults={
                    'title': alt_title.get('name'),
                    'language': language_obj,
                    'cover': cover_obj,
                    'description': alt_title.get('comment')
                }
            )

            lang_supports_obj.support_types.add(support_obj)
        except Exception:
            alt_title_obj = AlternativeTitle.objects.create(
                title=alt_title.get('name'),
                type=comment,
                game=igdb_data
            )
            alt_title_obj.save()

    # print(json.dumps(language_supports, indent=4))
    for language_support in language_supports:
        language: Dict = language_support.get('language')
        language_obj, _ = Language.objects.update_or_create(
            locale=language.get('locale'),
            defaults={
                'name': language.get('name'),
                'native_name': language.get('native_name')
            }
        )

        support: Dict = language_support.get('language_support_type')
        support_obj, support_created = SupportType.objects.update_or_create(
            name=support.get('name')
        )

        if support_created:
            support_obj.save()

        lang_supports_obj, _ = LanguageSupport.objects.get_or_create(
            game=igdb_data,
            language=language_obj,
            defaults={
                'title': None,
                'cover': None,
                'description': None,
            }
        )

        lang_supports_obj.support_types.add(support_obj)


def add_game_cover(game: Dict) -> Cover:
    """Add game's cover to game model

    Args:
        game (dict): Dictionary of the game

    Returns:
        Cover: _description_
    """
    game_title = game.get('name')
    if game.get('cover'):
        game_cover, game_cover_created = Cover.objects.get_or_create(
            filename=slugify(game_title),
            defaults={
                'url': game.get('cover').get('url'),
                'animated': game.get('cover', {}).get('animated'),
                'height': game.get('cover', {}).get('height'),
                'width': game.get('cover', {}).get('width')
            }
        )
    else:
        game_cover, game_cover_created = Cover.objects.get_or_create(
            url=game.get('cover', {}).get('url', 'http://127.0.0.1:8000/static/covers/None.jpg'),
            defaults={
                'filename': slugify(game_title),
                'animated': game.get('cover', {}).get('animated'),
                'height': game.get('cover', {}).get('height'),
                'width': game.get('cover', {}).get('width')
            }
        )
    if game_cover_created:
        game_cover.save()

    return game_cover


def add_game_related_data(igdb_data, game, related_model, related_data):
    """Add related data to game model

    Args:
        igdb_data (Game): Game model to populate
        game (Dict[str, Any]): Dictionary of the game
        related_model (ModelType): ModelType related to Game model used to get or create the object
        related_data (str): Attribute that should be contained in Game model
    """
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
    """Add age ratings to game model

    Args:
        igdb_data (Game): Game model to populate
        game (Dict[str, Any]): Dictionary of the game
    """
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
    """Add release dates to game model

    Args:
        igdb_data (Game): Game model to populate
        game (Dict[str, Any]): Dictionary of the game
    """
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
    """Command handled by Django

    Args:
        BaseCommand (Type): Parent of the class
    """

    def handle(self, *args, **options):
        """Function to handle the seed_model"""
        # clear_data()
        with open('ex.json', encoding="utf8") as json_file:
            data = json.load(json_file)
            seed_model(data)
        # clear_data()
        print("IGDB API was successfully added")
