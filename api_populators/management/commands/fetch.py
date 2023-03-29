import sys
from multiprocessing import Process
from typing import Dict, List, Optional

import requests

from api.models import AgeRating, Language, Platform, SupportType
from api_populators.models import PlatformType, Rating, RatingOrg
from main import settings


class IGDBAPI:
    BASE_URL = 'https://api.igdb.com/v4'
    HEADERS = {
        'Client-ID': settings.TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {settings.TWITCH_AUTH}',
        'Accept': 'application/json'
    }
    FIELDS = [
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
        'multiplayer_modes.platform.*',
        'player_perspectives.*',
        'status',
        'storyline',
        'summary',
        'videos.*',
        'websites.*'
    ]

    def _post_request(self, endpoint: str, data: str = 'fields *; limit 500;') -> Optional[List[Dict]]:
        response = requests.post(
            f'{self.BASE_URL}/' + endpoint.removeprefix('/'),
            data=data,
            headers=self.HEADERS,
        )
        if response.status_code != 200:
            print(f'Request "{response.url}" failed with status code {response.status_code}: {response.text}')
            sys.exit(1)
        return response.json()

    def fetch_games(self, offset: int = 0, limit: int = 100, ids: Optional[List[int]] = None) -> List[Dict]:
        """Fetch games from IGDB API

        Args:
            offset (int, optional): the offset used for extract multiple games. Defaults to 0.
            limit (int, optional): the limit the API has. Defaults to 100.
            ids (List[int], optional): the ids used to scrape instead of normal request. Defaults to None.

        Returns:
            List[Dict]: list of dictionaries of the fetched games
        """
        limit = f'limit {limit};'
        joined_fields = f'fields {",".join(self.FIELDS)};'
        where = 'where id = ' + ' | id = '.join([str(id) for id in ids]) + ';' if ids else ''
        data = f'{joined_fields}{limit}offset{offset};{where}'
        return self._post_request('/games', data)

    @classmethod
    def populate(cls):
        igdb_api = IGDBAPI()
        f1 = Process(target=igdb_api._populate_age_ratings())
        f1.start()
        f2 = Process(target=igdb_api._populate_languages())
        f2.start()
        f3 = Process(target=igdb_api._populate_platforms())
        f3.start()

        return igdb_api

    def _populate_age_ratings(self):
        for age_rating in self._post_request('age_ratings'):
            rating = Rating(int(age_rating['rating'])).label
            organization = AgeRating.Organizations(RatingOrg(int(age_rating['category'])).label)
            AgeRating.objects.get_or_create(
                rating=rating,
                organization=organization
            )

    def _populate_platforms(self):
        for platform in self._post_request('platforms'):
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

    def _populate_languages(self):
        for language in self._post_request('languages'):
            Language.objects.get_or_create(
                locale=language['locale'],
                defaults={
                    'name': language['name'],
                    'native_name': language['native_name']
                }
            )
