from django.test import TestCase
from .models import PlatformType

# Create your tests here.


class PlatformTest(TestCase):
    def test_type(self):
        platform_type = PlatformType(2)
        self.assertEqual(platform_type.name, 'ARCADE')
