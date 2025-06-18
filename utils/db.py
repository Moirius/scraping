import sqlite3
import os
import re
from utils.logger import logger

# 📁 Chemin vers la base de données SQLite
DB_PATH = os.path.join("data", "leads.sqlite")

# ✅ Regex simple pour emails valides
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def init_db():
    """Crée les tables nécessaires si elles n'existent pas."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Table principale : infos issues de Google Places
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entreprises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        place_id TEXT UNIQUE,
        nom TEXT,
        adresse TEXT,
        téléphone TEXT,
        site TEXT,
        note REAL,
        nombre_avis INTEGER,
        types TEXT,
        maps_url TEXT,
        ouvert BOOLEAN,
        horaires TEXT,
        résumé TEXT,
        prix INTEGER,
        date_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table secondaire : infos issues du site web
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS infos_web (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entreprise_id INTEGER,
        source TEXT,
        champ TEXT,
        valeur TEXT,
        date_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (entreprise_id) REFERENCES entreprises(id)
    );
    """)

    # Table des avis Google
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS avis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entreprise_id INTEGER,
        auteur TEXT,
        url TEXT,
        note INTEGER,
        texte TEXT,
        date_scraping TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (entreprise_id) REFERENCES entreprises(id)
    );
    """)

    conn.commit()
    conn.close()
    logger.info("✅ Base de données initialisée")


def save_leads(leads):
    """Insère les données d'entreprises sans doublons (place_id)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for lead in leads:
        try:
            cursor.execute("""
            INSERT OR IGNORE INTO entreprises (
                place_id, nom, adresse, téléphone, site, note, nombre_avis,
                types, maps_url, ouvert, horaires, résumé, prix
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                lead.get("place_id"),
                lead.get("nom"),
                lead.get("adresse"),
                lead.get("téléphone"),
                lead.get("site"),
                lead.get("note"),
                lead.get("nombre_avis"),
                ", ".join(lead.get("types") or []),
                lead.get("maps_url"),
                lead.get("ouvert"),
                "\n".join(lead.get("horaires") or []),
                lead.get("résumé"),
                lead.get("prix")
            ))
        except Exception as e:
            logger.error(f"❌ Erreur d'insertion entreprise : {e}", exc_info=True)

    conn.commit()
    conn.close()


def insert_infos_web(entreprise_id, infos):
    """Ajoute les données enrichies (emails, réseaux, etc.) à une entreprise donnée, avec validation."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for info in infos:
        champ = info.get("champ", "").lower()
        valeur = info.get("valeur", "").strip()
        source = info.get("source", "inconnu")

        if not valeur:
            continue

        # Valide l'email
        if champ == "email" and not EMAIL_REGEX.match(valeur):
            logger.warning(f"🚫 Email invalide ignoré : {valeur}")
            continue

        try:
            cursor.execute("""
                INSERT INTO infos_web (entreprise_id, source, champ, valeur)
                VALUES (?, ?, ?, ?)
            """, (
                entreprise_id,
                source,
                champ,
                valeur
            ))
        except Exception as e:
            logger.error(f"❌ Erreur d'insertion infos_web : {e}", exc_info=True)

    conn.commit()
    conn.close()


def insert_avis(entreprise_id, avis_list):
    """Insère une liste d'avis associés à une entreprise."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for avis in avis_list:
        try:
            cursor.execute("""
                INSERT INTO avis (entreprise_id, auteur, url, note, texte)
                VALUES (?, ?, ?, ?, ?)
            """, (
                entreprise_id,
                avis.get("author_name"),
                avis.get("author_url"),
                avis.get("rating"),
                avis.get("text")
            ))
        except Exception as e:
            logger.error(f"❌ Erreur d'insertion avis : {e}", exc_info=True)

    conn.commit()
    conn.close()


def has_infos_web(entreprise_id):
    """Vérifie si des infos web sont déjà présentes pour cette entreprise."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM infos_web WHERE entreprise_id = ?", (entreprise_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0
