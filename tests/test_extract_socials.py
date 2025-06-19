import requests
from scraping.extract_socials import extract_infos_from_site


class MockResponse:
    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


def test_extract_infos_from_site(monkeypatch):
    html = """
    <html>
        <a href='https://facebook.com/example'></a>
        <a href='https://instagram.com/example'></a>
        <a href='mailto:test@example.com'>email</a>
    </html>
    """

    def mock_get(url, timeout=8):
        return MockResponse(html)

    monkeypatch.setattr(requests, "get", mock_get)
    infos = extract_infos_from_site("http://dummy")
    champs = {(i["champ"], i["valeur"]) for i in infos}
    assert ("facebook", "https://facebook.com/example") in champs
    assert ("instagram", "https://instagram.com/example") in champs
    assert ("email", "test@example.com") in champs
