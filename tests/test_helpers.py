import pytest
from utils.helpers import is_valid_url

@pytest.mark.parametrize("url,expected", [
    ("https://example.com", True),
    ("http://example.com", True),
    ("ftp://example.com", False),
    ("not a url", False),
])
def test_is_valid_url(url, expected):
    assert is_valid_url(url) is expected
