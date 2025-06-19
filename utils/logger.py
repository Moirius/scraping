import logging
import sys

# Création du logger global
logger = logging.getLogger("scraper")
logger.setLevel(logging.INFO)

# Formatter avec timestamp + niveau + message
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

# Handler console avec encodage UTF-8
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Enregistre aussi les logs dans un fichier pour consultation
file_handler = logging.FileHandler("scraping.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Évite les doublons de logs
logger.propagate = False
