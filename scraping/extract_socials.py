import requests
from bs4 import BeautifulSoup
import re
from utils.logger import logger

# 🎯 Patterns de détection
SOCIAL_PATTERNS = {
    "facebook": r"(https?://(www\.)?facebook\.com/[^\s\"'>]+)",
    "instagram": r"(https?://(www\.)?instagram\.com/[^\s\"'>]+)",
    "linkedin": r"(https?://(www\.)?linkedin\.com/[^\s\"'>]+)",
    "youtube": r"(https?://(www\.)?youtube\.com/[^\s\"'>]+)",
    "tiktok": r"(https?://(www\.)?tiktok\.com/@[^\s\"'>]+)",
    "email": r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
}

def extract_infos_from_site(url):
    logger.info(f"🌐 Scraping site : {url}")
    infos = []

    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        html = soup.prettify()

        for champ, pattern in SOCIAL_PATTERNS.items():
            matches = re.findall(pattern, html)
            # Pour les tuples, on prend le premier élément
            cleaned = {match[0] if isinstance(match, tuple) else match for match in matches}
            for valeur in cleaned:
                infos.append({
                    "source": "site",
                    "champ": champ,
                    "valeur": valeur
                })

        if not infos:
            logger.warning(f"🔍 Aucun réseau social trouvé sur : {url}")

    except Exception as e:
        logger.error(f"❌ Erreur scraping site {url}", exc_info=True)
        infos.append({
            "source": "site",
            "champ": "scraping_error",
            "valeur": str(e)
        })

    return infos
