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

# Évite les doublons de logs
logger.propagate = False
