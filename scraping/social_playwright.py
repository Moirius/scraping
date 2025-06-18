from playwright.sync_api import sync_playwright
import time
import os
import glob


# --- INSTAGRAM ---
def scrape_instagram_profile(url, storage_path="cookie/ig_auth.json"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage_path)
        page = context.new_page()

        try:
            page.goto(url, timeout=30000)
            time.sleep(3)

            # Accepter les cookies
            try:
                accept_btn = page.locator("text=Accepter les cookies").first
                if accept_btn.is_visible():
                    accept_btn.click()
                    time.sleep(2)
            except:
                pass

            # Publications
            posts = None
            try:
                posts_text = page.locator(
                    "header section ul li:nth-child(1) span"
                ).first.inner_text(timeout=5000)
                posts = posts_text.strip()
            except:
                print("⚠️ Publications non trouvées")

            # Abonnés
            followers = None
            try:
                followers_span = page.locator(
                    "header section ul li:nth-child(2) span"
                ).first
                followers = followers_span.get_attribute(
                    "title"
                ) or followers_span.inner_text(timeout=5000)
            except:
                print("⚠️ Abonnés non trouvés")

            # Abonnements
            following = None
            try:
                following_span = page.locator(
                    "header section ul li:nth-child(3) span"
                ).first
                following = following_span.inner_text(timeout=5000).strip()
            except:
                print("⚠️ Abonnements non trouvés")

            return {"followers": followers, "following": following, "posts": posts}

        except Exception as e:
            print(f"⚠️ Erreur Instagram : {e}")
            return {"followers": None, "following": None, "posts": None}
        finally:
            browser.close()


# --- FACEBOOK ---
def scrape_facebook_page(url, storage_path="cookie/fb_auth.json", debug=False):
    screenshot_dir = "screenshots/facebook"
    os.makedirs(screenshot_dir, exist_ok=True)

    existing = glob.glob(os.path.join(screenshot_dir, "screenshot_fb_debug_*.png"))
    nums = [
        int(f.split("_")[-1].split(".")[0])
        for f in existing
        if f.split("_")[-1].split(".")[0].isdigit()
    ]
    next_num = max(nums) + 1 if nums else 1
    screenshot_path = os.path.join(
        screenshot_dir, f"screenshot_fb_debug_{next_num}.png"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage_path)
        page = context.new_page()

        try:
            print(f"🔍 Scraping de la page Facebook : {url}")
            page.goto(url, timeout=30000)

            try:
                accept_btn = page.locator("text=Autoriser tous les cookies").first
                if accept_btn.is_visible():
                    accept_btn.click()
                    time.sleep(2)
            except Exception as e:
                if debug:
                    print(f"ℹ️ Pas de bouton cookies à gérer : {e}")

            print("🔽 Scroll pour charger contenu...")
            for _ in range(2):
                page.mouse.wheel(0, 300)
                time.sleep(1)

            page.wait_for_timeout(2000)
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Capture enregistrée : {screenshot_path}")

            likes = None
            followers = None
            description = None
            email = None
            phone = None
            website = None
            address = None
            last_post = None
            has_video = False

            try:
                phone = page.locator("a[href^='tel']").first.inner_text()
                print(f"📞 Téléphone trouvé : {phone}")
            except Exception as e:
                print(f"❌ Pas de téléphone détecté : {e}")

            try:
                email = page.locator("a[href^='mailto']").first.inner_text()
                print(f"📧 Email trouvé : {email}")
            except Exception as e:
                print(f"❌ Pas d'email détecté : {e}")

            try:
                website = page.locator(
                    "a[href^='http']:not([href*='facebook'])"
                ).first.inner_text()
                print(f"🌐 Site web trouvé : {website}")
            except Exception as e:
                print(f"❌ Pas de site web détecté : {e}")

            try:
                address_block = page.locator(
                    "[aria-label*='adresse'], [data-pagelet*='ProfileTiles']"
                ).first
                if address_block:
                    full_text = address_block.inner_text()
                    for line in full_text.split("\n"):
                        if any(
                            keyword in line.lower()
                            for keyword in ["rue", "avenue", "place", "boulevard"]
                        ):
                            address = line.strip()
                            print(f"📍 Adresse trouvée : {address}")
                            break
            except Exception as e:
                print(f"❌ Pas d'adresse trouvée : {e}")

            # Fallback depuis des <span> visibles
            if not email:
                try:
                    email_span = page.locator("span", has_text="@").first
                    email_candidate = email_span.inner_text().strip()
                    if "@" in email_candidate and "." in email_candidate:
                        email = email_candidate
                        print(f"📧 Email détecté dans un span : {email}")
                except Exception as e:
                    print(f"❌ Email non détecté dans span : {e}")

            if not phone:
                try:
                    spans = page.locator("span")
                    for i in range(spans.count()):
                        txt = spans.nth(i).inner_text()
                        match = re.search(r"(0|\+33)[1-9](\s?\d{2}){4}", txt)
                        if match:
                            phone = match.group()
                            print(f"📞 Téléphone détecté dans un span : {phone}")
                            break
                except Exception as e:
                    print(f"❌ Téléphone non détecté dans span : {e}")

            full_text = page.inner_text("body")
            lines = [line.strip() for line in full_text.split("\n") if line.strip()]

            if debug:
                print("📄 Lignes de texte scrappées :")
                for l in lines:
                    print(f"→ {l}")

            for line in lines:
                lower = line.lower()
                if "j’aime" in lower and not likes:
                    likes = line
                    print(f"👍 Likes détectés : {likes}")
                if "abonnés" in lower and not followers:
                    followers = line
                    print(f"👥 Followers détectés : {followers}")
                if not email and "@" in line and "." in line:
                    email = line
                    print(f"📧 Email fallback : {email}")
                if not phone:
                    match = re.search(r"(0|\+33)[1-9](\s?\d{2}){4}", line)
                    if match:
                        phone = match.group()
                        print(f"📞 Téléphone fallback : {phone}")
                if not website and line.startswith("http") and "facebook" not in line:
                    website = line
                    print(f"🌐 Site fallback : {website}")

            try:
                video_blocks = page.locator("video")
                has_video = video_blocks.count() > 0
                print(f"🎥 Présence de vidéo : {has_video}")
            except Exception as e:
                print(f"❌ Erreur vérif vidéo : {e}")

            try:
                post_blocks = page.locator("div[role='article']")
                if post_blocks.count() > 0:
                    last_text = post_blocks.nth(0).inner_text()
                    time_tag = post_blocks.nth(0).locator("time")
                    post_date = (
                        time_tag.get_attribute("datetime")
                        if time_tag.count() > 0
                        else None
                    )
                    last_post = {"text": last_text[:300], "date": post_date}
                    print(f"🗞️ Dernier post : {last_post}")
            except Exception as e:
                print(f"❌ Erreur extraction post : {e}")

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
                "screenshot": screenshot_path,
            }

        except Exception as e:
            print(f"⚠️ Erreur Facebook : {e}")
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Capture d'erreur enregistrée : {screenshot_path}")
            return {}
        finally:
            browser.close()
