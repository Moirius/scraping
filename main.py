import os
import re
import sqlite3


from utils.db import init_db, save_leads, insert_infos_web, insert_avis, has_infos_web
from scraping.search_google import search_google_places
from scraping.extract_socials import extract_infos_from_site
from scraping.social_playwright import scrape_instagram_profile, scrape_facebook_page
from utils.logger import logger
from utils.helpers import is_valid_url


DB_PATH = os.path.join("data", "leads.sqlite")


def is_valid_url(url):
    return url and url.startswith("http") and re.match(r"^https?://[^\s]+$", url)


if __name__ == "__main__":
    logger.info("🚀 Démarrage du script principal")
    init_db()

    keyword = "restauration"
    city = "Rennes"
    target_count = 5

    logger.info(f"🔍 Scraping Google Places API pour '{keyword}' à {city}")
    bruts = search_google_places(keyword, city, max_results=20)

    results = []
    for lead in bruts:
        place_id = lead.get("place_id")
        if not place_id:
            continue

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM entreprises WHERE place_id = ?", (place_id,))
        exists = cursor.fetchone()
        conn.close()

        if exists:
            logger.info(f"⏭️ Déjà en base : {lead.get('nom')}")
            continue

        results.append(lead)
        logger.info(f"✅ Nouvelle entreprise : {lead.get('nom')}")
        if len(results) >= target_count:
            break

    logger.info(f"🎯 {len(results)} entreprise(s) à insérer.")
    save_leads(results)

    for res in results:
        print("✅ Entreprise trouvée :")
        for k, v in res.items():
            print(f"  {k}: {v}")
        print("-----")

    logger.info("🌐 Scraping des sites web pour extraire les réseaux sociaux et emails")

    for lead in results:
        site = lead.get("site")
        place_id = lead.get("place_id")
        avis = lead.get("avis", [])

        if not place_id:
            logger.warning("⚠️ place_id manquant, on ignore ce lead")
            continue

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM entreprises WHERE place_id = ?", (place_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            logger.warning(f"❌ Aucune entreprise trouvée en base pour le place_id {place_id}")
            continue

        entreprise_id = row[0]

        if avis:
            insert_avis(entreprise_id, avis)
            logger.info(f"📝 {len(avis)} avis inséré(s) pour l’entreprise ID {entreprise_id}")
        else:
            logger.info(f"ℹ️ Aucun avis à insérer pour l’entreprise ID {entreprise_id}")

        if site and ("instagram.com" in site or "facebook.com" in site):
            infos = []

            if "instagram.com" in site:
                try:
                    insta_stats = scrape_instagram_profile(site)
                    if insta_stats:
                        infos += [
                            {"champ": "instagram", "valeur": site, "source": "site_direct"},
                            {"champ": "ig_followers", "valeur": insta_stats["followers"], "source": "instagram"},
                            {"champ": "ig_following", "valeur": insta_stats["following"], "source": "instagram"},
                            {"champ": "ig_posts", "valeur": insta_stats["posts"], "source": "instagram"},
                        ]
                        logger.info(f"📊 Stats Instagram (site direct) insérées pour ID {entreprise_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Scraping Instagram direct échoué pour {site} : {e}")

            if "facebook.com" in site:
                try:
                    fb_stats = scrape_facebook_page(site)
                    if fb_stats:
                        infos += [{"champ": "facebook", "valeur": site, "source": "site_direct"}]
                        if fb_stats.get("followers"):
                            infos.append({"champ": "fb_followers", "valeur": fb_stats["followers"], "source": "facebook"})
                        if fb_stats.get("likes"):
                            infos.append({"champ": "fb_likes", "valeur": fb_stats["likes"], "source": "facebook"})
                        logger.info(f"📘 Stats Facebook (site direct) insérées pour ID {entreprise_id}")
                except Exception as e:
                    logger.warning(f"⚠️ Scraping Facebook direct échoué pour {site} : {e}")

            insert_infos_web(entreprise_id, infos)
            continue

        if not site:
            logger.info(f"🌐 Aucun site pour {lead.get('nom')}, on saute le scraping web.")
            continue

        if has_infos_web(entreprise_id):
            logger.info(f"⏩ Infos déjà présentes pour l’entreprise ID {entreprise_id}, on saute.")
            continue

        try:
            logger.info(f"🌐 Scraping site : {site}")
            infos = extract_infos_from_site(site)
            insert_infos_web(entreprise_id, infos)
            logger.info(f"📩 Infos web insérées pour l’entreprise ID {entreprise_id}")

            # 🔍 Scraping Instagram & Facebook si lien trouvé
            # 🔍 Scraping Instagram & Facebook si lien trouvé
            for info in infos:
                if info["champ"] == "instagram":
                    insta_url = info["valeur"]
                    try:
                        insta_stats = scrape_instagram_profile(insta_url)
                        if insta_stats:
                            insta_infos = [
                                {"champ": "ig_followers", "valeur": insta_stats["followers"], "source": "instagram"},
                                {"champ": "ig_following", "valeur": insta_stats["following"], "source": "instagram"},
                                {"champ": "ig_posts", "valeur": insta_stats["posts"], "source": "instagram"},
                            ]
                            insert_infos_web(entreprise_id, insta_infos)
                            logger.info(f"📊 Stats Instagram insérées pour l’entreprise ID {entreprise_id}")
                    except Exception as e:
                        logger.warning(f"⚠️ Scraping Instagram échoué pour {insta_url} : {e}")

                if info["champ"] == "facebook":
                    fb_url = info["valeur"]
                    try:
                        fb_stats = scrape_facebook_page(fb_url)
                        if fb_stats:
                            fb_infos = []
                            if fb_stats.get("followers"):
                                fb_infos.append({"champ": "fb_followers", "valeur": fb_stats["followers"], "source": "facebook"})
                            if fb_stats.get("likes"):
                                fb_infos.append({"champ": "fb_likes", "valeur": fb_stats["likes"], "source": "facebook"})
                            if fb_stats.get("email"):
                                fb_infos.append({"champ": "email", "valeur": fb_stats["email"], "source": "facebook"})
                            if fb_stats.get("phone"):
                                fb_infos.append({"champ": "tel", "valeur": fb_stats["phone"], "source": "facebook"})
                            if fb_stats.get("address"):
                                fb_infos.append({"champ": "adresse", "valeur": fb_stats["address"], "source": "facebook"})

                            if fb_infos:
                                insert_infos_web(entreprise_id, fb_infos)
                                logger.info(f"📘 Stats Facebook insérées pour l’entreprise ID {entreprise_id}")

                            if fb_stats.get("website"):
                                website = fb_stats["website"]

                                # 🔁 Éviter les boucles infinies : ne pas re-scraper si c’est le site initial
                                if website.strip("/") == site.strip("/"):
                                    logger.info("♻️ Site web déjà scrappé, on évite la boucle.")
                                    continue

                                # ✅ Vérification d'URL valide
                                if not is_valid_url(website):
                                    logger.warning(f"⚠️ URL invalide ignorée : {website}")
                                    continue

                                logger.info(f"🌐 Site web trouvé sur Facebook : {website}")
                                try:
                                    website_infos = extract_infos_from_site(website)
                                    if website_infos:
                                        insert_infos_web(entreprise_id, website_infos)
                                        logger.info(f"💾 Infos site web insérées pour l’entreprise ID {entreprise_id}")
                                except Exception as e:
                                    logger.warning(f"⚠️ Scraping site web depuis Facebook échoué : {e}")
                    except Exception as e:
                        logger.warning(f"⚠️ Scraping Facebook échoué pour {fb_url} : {e}")



        except Exception:
            logger.error(f"💥 Erreur scraping site {site}", exc_info=True)

    logger.info("✅ Script terminé")
