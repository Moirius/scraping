import os
from scraping.search_google import search_google_places
import requests

class DummyResp:
    def __init__(self, data):
        self._data = data
    def json(self):
        return self._data
    def raise_for_status(self):
        pass


def test_search_google_places(monkeypatch):
    os.environ['GOOGLE_PLACES_API_KEY'] = 'dummy'

    calls = []
    def mock_get(url, params=None):
        calls.append(url)
        if 'textsearch' in url:
            return DummyResp({'results': [{'place_id': 'abc123'}]})
        else:
            return DummyResp({'result': {'name': 'Test',
                                        'formatted_address': 'Add',
                                        'formatted_phone_number': '123',
                                        'website': 'https://example.com',
                                        'rating': 4.5,
                                        'user_ratings_total': 10,
                                        'types': ['type'],
                                        'url': 'maps_url',
                                        'opening_hours': {'open_now': True, 'weekday_text': []},
                                        'editorial_summary': {'overview': 'ok'},
                                        'reviews': [],
                                        'price_level': 2,
                                        'photos': []}})
    monkeypatch.setattr(requests, 'get', mock_get)
    leads = search_google_places('foo', 'bar', max_results=1)
    assert len(leads) == 1
    lead = leads[0]
    assert lead['place_id'] == 'abc123'
    assert lead['nom'] == 'Test'
    assert lead['site'] == 'https://example.com'
