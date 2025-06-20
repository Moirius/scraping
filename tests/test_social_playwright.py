import json
import os
from scraping.social_playwright import scrape_instagram_profile
import requests

class DummyResp:
    def __init__(self, data):
        self._data = data
    def json(self):
        return self._data
    def raise_for_status(self):
        pass


def test_scrape_instagram_profile(tmp_path, monkeypatch):
    # create fake cookie file
    cookie = {"cookies": [{"name": "sessionid", "value": "x", "domain": ".instagram.com", "path": "/"}]}
    cookie_file = tmp_path / "ig.json"
    cookie_file.write_text(json.dumps(cookie))

    def mock_get(url, headers=None, cookies=None, timeout=15):
        assert "web_profile_info" in url
        return DummyResp({"data": {"user": {
            "edge_followed_by": {"count": 5},
            "edge_follow": {"count": 2},
            "edge_owner_to_timeline_media": {"count": 7}
        }}})

    monkeypatch.setattr(requests, "get", mock_get)
    res = scrape_instagram_profile("https://www.instagram.com/test/", storage_path=str(cookie_file))
    assert res == {"followers": 5, "following": 2, "posts": 7}
