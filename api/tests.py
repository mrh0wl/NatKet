from datetime import datetime
from django.test import TestCase

from api.models import AgeRating, Game, AlternativeName


class GameTestCase(TestCase):
    def setUp(self):
        self.age_rating = AgeRating.objects.create(
            organization=AgeRating.Organizations.ESRB,
            rating='M'
        )
        self.game = Game.objects.create(
            title='Testing',
            slug='testing',
            age_rating=self.age_rating,
            game_type=Game.GameType.MAINGAME,
            release_date=datetime.now()
        )
        # self.game.age_rating.add(self.age_rating)
        self.alt_name1 = AlternativeName.objects.create(
            name='Test',
            lang=u'Español',
            game=self.game
        )
        self.alt_name2 = AlternativeName.objects.create(
            name='Test2',
            lang=u'Portugues',
            game=self.game
        )

    def test_age_rating_org(self):
        """ Age Rating Organization can be show correctly """
        pegi = AgeRating.objects.get(organization=AgeRating.Organizations.ESRB)
        self.assertEqual(
            pegi.organization,
            "ESRB"
        )

    def test_game(self):
        game = Game.objects.get(title='Testing')
        title = game.title
        slug = game.slug
        game_type = game.game_type
        age_rating: AgeRating = game.age_rating
        alt_names = list(game.alternative_names.all())
        self.assertEqual(
            title,
            "Testing"
        )
        self.assertEqual(
            slug,
            "testing"
        )
        self.assertEqual(
            game_type,
            Game.GameType.MAINGAME
        )
        self.assertEqual(
            age_rating,
            self.age_rating
        )
        self.assertQuerysetEqual(
            alt_names,
            [self.alt_name2, self.alt_name1]
        )
        
