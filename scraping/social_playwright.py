import json
import os
import re
import glob
import time
from playwright.sync_api import sync_playwright
import requests
from utils.logger import logger


def refresh_instagram_session(storage_path="cookie/ig_auth.json"):
    """Login automatiquement à Instagram pour régénérer le fichier cookie."""
    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")

    if not username or not password:
        logger.warning("⚠️ IG_USERNAME ou IG_PASSWORD manquant pour rafraîchir la session Instagram")
        return False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://www.instagram.com/accounts/login/", timeout=60000)
            page.fill("input[name='username']", username)
            page.fill("input[name='password']", password)
            page.click("button[type='submit']")
            page.wait_for_url("https://www.instagram.com/", timeout=120000)
            context.storage_state(path=storage_path)
            browser.close()
        logger.info("✅ Session Instagram rafraîchie")
        return True
    except Exception as e:
        logger.error(f"❌ Impossible de rafraîchir la session Instagram : {e}")
        return False


def refresh_facebook_session(storage_path="cookie/fb_auth.json"):
    """Login automatiquement à Facebook pour régénérer le fichier cookie."""
    username = os.getenv("FB_USERNAME")
    password = os.getenv("FB_PASSWORD")

    if not username or not password:
        logger.warning("⚠️ FB_USERNAME ou FB_PASSWORD manquant pour rafraîchir la session Facebook")
        return False

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto("https://www.facebook.com/login", timeout=60000)
            page.fill("input[name='email']", username)
            page.fill("input[name='pass']", password)
            page.click("button[name='login']")
            page.wait_for_url(re.compile("facebook.com"), timeout=120000)
            context.storage_state(path=storage_path)
            browser.close()
        logger.info("✅ Session Facebook rafraîchie")
        return True
    except Exception as e:
        logger.error(f"❌ Impossible de rafraîchir la session Facebook : {e}")
        return False


# --- INSTAGRAM ---
def scrape_instagram_profile(url, storage_path="cookie/ig_auth.json"):
    """Récupère les statistiques d'un profil Instagram via l'API web."""
    username = url.rstrip("/").split("/")[-1].split("?")[0]

    if not os.path.exists(storage_path):
        refresh_instagram_session(storage_path)

    # Charge les cookies Playwright si disponibles
    cookies = []
    if os.path.exists(storage_path):
        try:
            with open(storage_path, "r", encoding="utf-8") as f:
                cookies_data = json.load(f)
                cookies = cookies_data.get("cookies", [])
        except Exception as e:
            logger.warning(f"⚠️ Impossible de lire les cookies Instagram : {e}")

    jar = requests.cookies.RequestsCookieJar()
    for c in cookies:
        jar.set(c.get("name"), c.get("value"), domain=c.get("domain"), path=c.get("path"))

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-IG-App-ID": "936619743392459",
    }

    api_url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"

    try:
        resp = requests.get(api_url, headers=headers, cookies=jar, timeout=15)
        if getattr(resp, "status_code", 200) == 401:
            logger.info("🔄 Session Instagram invalide, tentative de rafraîchissement")
            if refresh_instagram_session(storage_path):
                with open(storage_path, "r", encoding="utf-8") as f:
                    cookies_data = json.load(f)
                jar = requests.cookies.RequestsCookieJar()
                for c in cookies_data.get("cookies", []):
                    jar.set(c.get("name"), c.get("value"), domain=c.get("domain"), path=c.get("path"))
                resp = requests.get(api_url, headers=headers, cookies=jar, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        user = data.get("data", {}).get("user", {})
        return {
            "followers": user.get("edge_followed_by", {}).get("count"),
            "following": user.get("edge_follow", {}).get("count"),
            "posts": user.get("edge_owner_to_timeline_media", {}).get("count"),
        }
    except Exception as e:
        logger.error(f"⚠️ Erreur Instagram : {e}")
        return {
            "followers": None,
            "following": None,
            "posts": None,
        }

def scrape_facebook_page(url, storage_path="cookie/fb_auth.json", debug=False):
    import os, re, glob, time
    from playwright.sync_api import sync_playwright

    screenshot_dir = "screenshots/facebook"
    os.makedirs(screenshot_dir, exist_ok=True)

    existing = glob.glob(os.path.join(screenshot_dir, "screenshot_fb_debug_*.png"))
    nums = [int(f.split("_")[-1].split(".")[0]) for f in existing if f.split("_")[-1].split(".")[0].isdigit()]
    next_num = max(nums) + 1 if nums else 1
    screenshot_path = os.path.join(screenshot_dir, f"screenshot_fb_debug_{next_num}.png")

    if not os.path.exists(storage_path):
        refresh_facebook_session(storage_path)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage_path, ignore_https_errors=True)
        page = context.new_page()

        try:
            logger.info(f"🔍 Scraping de la page Facebook : {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
            if "login" in page.url:
                logger.info("🔄 Session Facebook invalide, tentative de rafraîchissement")
                if refresh_facebook_session(storage_path):
                    context = browser.new_context(storage_state=storage_path, ignore_https_errors=True)
                    page = context.new_page()
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    time.sleep(5)

            try:
                accept_btn = page.locator("text=Autoriser tous les cookies").first
                if accept_btn.is_visible():
                    accept_btn.click()
                    time.sleep(2)
            except Exception as e:
                if debug:
                    logger.info(f"ℹ️ Pas de bouton cookies à gérer : {e}")

            logger.info("🔽 Scroll pour charger contenu...")
            for _ in range(2):
                page.mouse.wheel(0, 300)
                time.sleep(1)

            page.wait_for_timeout(2000)
            page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"📸 Capture enregistrée : {screenshot_path}")

            likes = None
            followers = None
            email = None
            phone = None
            website = None
            address = None
            last_post = None
            has_video = False

            full_text = page.inner_text("body")
            lines = [line.strip() for line in full_text.split("\n") if line.strip()]

            # 📧 Email
            match_email = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", full_text)
            if match_email:
                email = match_email.group()
                logger.info(f"📧 Email trouvé : {email}")

            # 📞 Téléphone
            match_phone = re.search(r"(0|\+33)[1-9](\s?\d{2}){4}", full_text)
            if match_phone:
                phone = match_phone.group()
                logger.info(f"📞 Téléphone trouvé : {phone}")

            # 🌐 Site web
            urls = [line for line in lines if line.startswith("http") and "facebook.com" not in line]
            for link in urls:
                if not any(word in link for word in ["reserve", "dish.co", "tripadvisor"]):
                    website = link
                    break
            if not website and urls:
                website = urls[0]
            if not website:
                for line in lines:
                    if "." in line and "facebook.com" not in line and "@" not in line and len(line) < 60:
                        website = "https://" + line.strip()
                        logger.info(f"🌐 Site web fallback : {website}")
                        break
            if website:
                logger.info(f"🌐 Site web trouvé : {website}")

            # 🏠 Adresse
            for line in lines:
                if len(line) < 100 and re.search(r"\d+ .*?(rue|avenue|boulevard|place|impasse|allée|france)", line.lower()):
                    address = line.strip()
                    logger.info(f"📍 Adresse trouvée : {address}")
                    break

            # 👍 Likes & Followers
            match_likes_followers = re.search(r"([\d\s,.Kk]+)\s*J’aime\s*•\s*([\d\s,.Kk]+)\s*followers", full_text)
            if match_likes_followers:
                likes = match_likes_followers.group(1).strip()
                followers = match_likes_followers.group(2).strip()
                logger.info(f"👍 Likes : {likes}")
                logger.info(f"👥 Followers : {followers}")
            else:
                for line in lines:
                    if "j’aime" in line.lower() and not likes:
                        likes = line.strip()
                        logger.info(f"👍 Likes : {likes}")
                    if "followers" in line.lower() and not followers:
                        followers = line.strip()
                        logger.info(f"👥 Followers : {followers}")

            # 🎥 Présence de vidéo
            try:
                video_tags = page.locator("video")
                iframe_tags = page.locator("iframe[src*='video']")
                has_video = video_tags.count() > 0 or iframe_tags.count() > 0
                logger.info(f"🎥 Présence de vidéo : {has_video}")
            except Exception as e:
                logger.warning(f"❌ Erreur vérif vidéo : {e}")

            # 🗞️ Dernier post
            try:
                post_blocks = page.locator("div[role='article']")
                for i in range(min(post_blocks.count(), 5)):
                    last_text = post_blocks.nth(i).inner_text().strip()
                    time_tag = post_blocks.nth(i).locator("time")
                    post_date = time_tag.get_attribute("datetime") if time_tag.count() > 0 else None

                    if len(last_text) > 50:
                        last_post = {
                            "text": last_text[:300],
                            "date": post_date
                        }
                        logger.info(f"🗞️ Dernier post : {last_post}")
                        break
            except Exception as e:
                logger.warning(f"❌ Erreur extraction post : {e}")

            if debug:
                logger.debug("📄 Lignes de texte scrappées :")
                for l in lines:
                    logger.debug(f"→ {l}")

            with open("debug_facebook_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())

            return {
                "likes": likes,
                "followers": followers,
                "email": email,
                "phone": phone,
                "website": website,
                "address": address,
                "has_video": has_video,
                "last_post": last_post,
                "screenshot": screenshot_path
            }

        except Exception as e:
            logger.error(f"⚠️ Erreur Facebook : {e}")
            page.screenshot(path=screenshot_path, full_page=True)
            logger.error(f"📸 Capture d'erreur enregistrée : {screenshot_path}")
            return {}
        finally:
            browser.close()
