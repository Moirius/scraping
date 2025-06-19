import os
import sqlite3
import tempfile

import utils.db as db


def setup_temp_db(tmp_path):
    db.DB_PATH = os.path.join(tmp_path, "test.sqlite")
    db.init_db()


def test_save_and_has_infos_web(tmp_path):
    setup_temp_db(tmp_path)
    lead = {
        "place_id": "1",
        "nom": "Test",
        "adresse": "Rue",
        "téléphone": "",
        "site": "",
        "note": 5,
        "nombre_avis": 1,
        "types": ["test"],
        "maps_url": "",
        "ouvert": True,
        "horaires": [],
        "résumé": "",
        "prix": 1,
    }
    db.save_leads([lead])
    conn = sqlite3.connect(db.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM entreprises WHERE place_id='1'")
    row = cursor.fetchone()
    assert row is not None
    entreprise_id = row[0]
    infos = [
        {"source": "site", "champ": "email", "valeur": "test@example.com"},
        {"source": "site", "champ": "facebook", "valeur": "https://fb.com"},
    ]
    db.insert_infos_web(entreprise_id, infos)
    assert db.has_infos_web(entreprise_id) is True
    cursor.execute("SELECT champ, valeur FROM infos_web")
    rows = cursor.fetchall()
    assert ("email", "test@example.com") in rows
    assert ("facebook", "https://fb.com") in rows
    conn.close()
