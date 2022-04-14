from django.test import TestCase
from httmock import HTTMock, all_requests
from djangoAdverity.utils import merge_and_transform


# no extensive test. Only one class for everything. Mostly here to help me develop
class Tests(TestCase):
    def test_fetch_data_404(self):
        """
        if swapi sending us 404, we send our user 503
        """
        # mocking swapi
        @all_requests
        def response_content(url, request):
            return {'status_code': 404,
                    'text': 'hi'}

        with HTTMock(response_content):
            r = self.client.get("/swapi/")
            self.assertEqual(r.status_code, 503)

    def test_merge_and_transform(self):
        people = [
            {
                "name": "Luke Skywalker",
                "height": "172",
                "mass": "77",
                "hair_color": "blond",
                "skin_color": "fair",
                "eye_color": "blue",
                "birth_year": "19BBY",
                "gender": "male",
                "homeworld": "https://swapi.dev/api/planets/1/",
                "films": [
                    "https://swapi.dev/api/films/1/",
                    "https://swapi.dev/api/films/2/",
                    "https://swapi.dev/api/films/3/",
                    "https://swapi.dev/api/films/6/"
                ],
                "species": [],
                "vehicles": [
                    "https://swapi.dev/api/vehicles/14/",
                    "https://swapi.dev/api/vehicles/30/"
                ],
                "starships": [
                    "https://swapi.dev/api/starships/12/",
                    "https://swapi.dev/api/starships/22/"
                ],
                "created": "2014-12-09T13:50:51.644000Z",
                "edited": "2014-12-20T21:17:56.891000Z",
                "url": "https://swapi.dev/api/people/1/"
            },
            {
                "name": "C-3PO",
                "height": "167",
                "mass": "75",
                "hair_color": "n/a",
                "skin_color": "gold",
                "eye_color": "yellow",
                "birth_year": "112BBY",
                "gender": "n/a",
                "homeworld": "https://swapi.dev/api/planets/2/",
                "films": [
                    "https://swapi.dev/api/films/1/",
                    "https://swapi.dev/api/films/2/",
                    "https://swapi.dev/api/films/3/",
                    "https://swapi.dev/api/films/4/",
                    "https://swapi.dev/api/films/5/",
                    "https://swapi.dev/api/films/6/"
                ],
                "species": [
                    "https://swapi.dev/api/species/2/"
                ],
                "vehicles": [],
                "starships": [],
                "created": "2014-12-10T15:10:51.357000Z",
                "edited": "2014-12-20T21:17:50.309000Z",
                "url": "https://swapi.dev/api/people/2/"
            }
        ]

        planets = [
            {
                "name": "Tatooine",
                "rotation_period": "23",
                "orbital_period": "304",
                "diameter": "10465",
                "climate": "arid",
                "gravity": "1 standard",
                "terrain": "desert",
                "surface_water": "1",
                "population": "200000",
                "residents": [
                    "https://swapi.dev/api/people/1/",
                    "https://swapi.dev/api/people/2/",
                    "https://swapi.dev/api/people/4/",
                    "https://swapi.dev/api/people/6/",
                    "https://swapi.dev/api/people/7/",
                    "https://swapi.dev/api/people/8/",
                    "https://swapi.dev/api/people/9/",
                    "https://swapi.dev/api/people/11/",
                    "https://swapi.dev/api/people/43/",
                    "https://swapi.dev/api/people/62/"
                ],
                "films": [
                    "https://swapi.dev/api/films/1/",
                    "https://swapi.dev/api/films/3/",
                    "https://swapi.dev/api/films/4/",
                    "https://swapi.dev/api/films/5/",
                    "https://swapi.dev/api/films/6/"
                ],
                "created": "2014-12-09T13:50:49.641000Z",
                "edited": "2014-12-20T20:58:18.411000Z",
                "url": "https://swapi.dev/api/planets/1/"
            },
            {
                "name": "Alderaan",
                "rotation_period": "24",
                "orbital_period": "364",
                "diameter": "12500",
                "climate": "temperate",
                "gravity": "1 standard",
                "terrain": "grasslands, mountains",
                "surface_water": "40",
                "population": "2000000000",
                "residents": [
                    "https://swapi.dev/api/people/5/",
                    "https://swapi.dev/api/people/68/",
                    "https://swapi.dev/api/people/81/"
                ],
                "films": [
                    "https://swapi.dev/api/films/1/",
                    "https://swapi.dev/api/films/6/"
                ],
                "created": "2014-12-10T11:35:48.479000Z",
                "edited": "2014-12-20T20:58:18.420000Z",
                "url": "https://swapi.dev/api/planets/2/"
            }
        ]

        expected_dict = [
            {'name': 'Luke Skywalker',
             'height': '172', 'mass': '77',
             'hair_color': 'blond',
             'skin_color': 'fair',
             'eye_color': 'blue',
             'birth_year': '19BBY',
             'gender': 'male',
             'homeworld': 'Tatooine',
             'date': '2014-12-20'
             },
            {'name': 'C-3PO',
             'height': '167',
             'mass': '75',
             'hair_color': 'n/a',
             'skin_color': 'gold',
             'eye_color': 'yellow',
             'birth_year': '112BBY',
             'gender': 'n/a',
             'homeworld': 'Alderaan',
             'date': '2014-12-20'}
        ]
        res = merge_and_transform(people, planets)
        self.assertEqual(res, expected_dict)
