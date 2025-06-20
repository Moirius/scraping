from scraping.extract_socials import extract_infos_from_site
import requests

class DummyResponse:
    def __init__(self, text):
        self.text = text
    def raise_for_status(self):
        pass


def test_extract_infos_from_site(monkeypatch):
    html = """
        <html>
            <body>
                <a href='https://facebook.com/testpage'>fb</a>
                <a href='https://www.instagram.com/test/'>ig</a>
                <a href='mailto:contact@example.com'>email</a>
            </body>
        </html>
    """
    def mock_get(url, timeout=8):
        return DummyResponse(html)
    monkeypatch.setattr(requests, "get", mock_get)
    infos = extract_infos_from_site("https://example.com")
    champs = {i["champ"] for i in infos}
    assert "facebook" in champs
    assert "instagram" in champs
    assert "email" in champs
