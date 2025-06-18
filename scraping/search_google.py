import os
import requests
from dotenv import load_dotenv
from utils.logger import logger

# 🔐 Chargement des variables d'environnement
load_dotenv()
API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

if not API_KEY:
    logger.critical("❌ Clé API Google Places absente dans le .env")
    raise ValueError("Clé API Google Places manquante dans .env")

logger.info("🔐 Clé API Google chargée avec succès")

def search_google_places(keyword, city, max_results=10):
    logger.info(f"🔎 Recherche Google Places : '{keyword}' à '{city}' (max {max_results})")

    query = f"{keyword} {city}"
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": API_KEY,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        places = response.json().get("results", [])[:max_results]
    except Exception as e:
        logger.error("❌ Erreur lors de l'appel à Text Search API", exc_info=True)
        return []

    leads = []

    for place in places:
        place_id = place.get("place_id")
        if not place_id:
            logger.warning("⚠️ place_id manquant, on ignore ce résultat")
            continue

        # Appel aux détails
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        details_params = {
            "place_id": place_id,
            "key": API_KEY,
            "fields": (
                "name,formatted_address,formatted_phone_number,"
                "international_phone_number,website,opening_hours,"
                "current_opening_hours,photos,editorial_summary,"
                "rating,user_ratings_total,types,url,reviews,price_level"
            )
        }

        try:
            details_response = requests.get(details_url, params=details_params)
            details_response.raise_for_status()
            details = details_response.json().get("result", {})
        except Exception as e:
            logger.error(f"❌ Erreur détails pour place_id {place_id}", exc_info=True)
            continue

        if not details.get("website"):
            logger.warning(f"⚠️ Aucun site web pour {details.get('name')}")

        leads.append({
            "place_id": place_id,
            "nom": details.get("name"),
            "adresse": details.get("formatted_address"),
            "téléphone": details.get("formatted_phone_number"),
            "site": details.get("website"),
            "note": details.get("rating"),
            "nombre_avis": details.get("user_ratings_total"),
            "types": details.get("types"),
            "maps_url": details.get("url"),
            "ouvert": details.get("opening_hours", {}).get("open_now"),
            "horaires": details.get("opening_hours", {}).get("weekday_text"),
            "résumé": details.get("editorial_summary", {}).get("overview"),
            "avis": details.get("reviews", []),
            "prix": details.get("price_level"),
            "photos": details.get("photos", [])
        })

    logger.info(f"✅ {len(leads)} entreprise(s) récupérée(s) depuis Google Places")
    return leads
