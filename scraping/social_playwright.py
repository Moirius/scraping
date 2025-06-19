from playwright.sync_api import sync_playwright
import time
import os
import glob
import re


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
                posts_text = page.locator("header section ul li:nth-child(1) span").first.inner_text(timeout=5000)
                posts = posts_text.strip()
            except:
                print("⚠️ Publications non trouvées")

            # Abonnés
            followers = None
            try:
                followers_span = page.locator("header section ul li:nth-child(2) span").first
                followers = followers_span.get_attribute("title") or followers_span.inner_text(timeout=5000)
            except:
                print("⚠️ Abonnés non trouvés")

            # Abonnements
            following = None
            try:
                following_span = page.locator("header section ul li:nth-child(3) span").first
                following = following_span.inner_text(timeout=5000).strip()
            except:
                print("⚠️ Abonnements non trouvés")

            return {
                "followers": followers,
                "following": following,
                "posts": posts
            }

        except Exception as e:
            print(f"⚠️ Erreur Instagram : {e}")
            return {
                "followers": None,
                "following": None,
                "posts": None
            }
        finally:
            browser.close()

def scrape_facebook_page(url, storage_path="cookie/fb_auth.json", debug=False):
    import os, re, glob, time
    from playwright.sync_api import sync_playwright

    screenshot_dir = "screenshots/facebook"
    os.makedirs(screenshot_dir, exist_ok=True)

    existing = glob.glob(os.path.join(screenshot_dir, "screenshot_fb_debug_*.png"))
    nums = [int(f.split("_")[-1].split(".")[0]) for f in existing if f.split("_")[-1].split(".")[0].isdigit()]
    next_num = max(nums) + 1 if nums else 1
    screenshot_path = os.path.join(screenshot_dir, f"screenshot_fb_debug_{next_num}.png")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage_path)
        page = context.new_page()

        try:
            print(f"🔍 Scraping de la page Facebook : {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)

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
                print(f"📧 Email trouvé : {email}")

            # 📞 Téléphone
            match_phone = re.search(r"(0|\+33)[1-9](\s?\d{2}){4}", full_text)
            if match_phone:
                phone = match_phone.group()
                print(f"📞 Téléphone trouvé : {phone}")

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
                        print(f"🌐 Site web fallback : {website}")
                        break
            if website:
                print(f"🌐 Site web trouvé : {website}")

            # 🏠 Adresse
            for line in lines:
                if len(line) < 100 and re.search(r"\d+ .*?(rue|avenue|boulevard|place|impasse|allée|france)", line.lower()):
                    address = line.strip()
                    print(f"📍 Adresse trouvée : {address}")
                    break

            # 👍 Likes & Followers
            match_likes_followers = re.search(r"([\d\s,.Kk]+)\s*J’aime\s*•\s*([\d\s,.Kk]+)\s*followers", full_text)
            if match_likes_followers:
                likes = match_likes_followers.group(1).strip()
                followers = match_likes_followers.group(2).strip()
                print(f"👍 Likes : {likes}")
                print(f"👥 Followers : {followers}")
            else:
                for line in lines:
                    if "j’aime" in line.lower() and not likes:
                        likes = line.strip()
                        print(f"👍 Likes : {likes}")
                    if "followers" in line.lower() and not followers:
                        followers = line.strip()
                        print(f"👥 Followers : {followers}")

            # 🎥 Présence de vidéo
            try:
                video_tags = page.locator("video")
                iframe_tags = page.locator("iframe[src*='video']")
                has_video = video_tags.count() > 0 or iframe_tags.count() > 0
                print(f"🎥 Présence de vidéo : {has_video}")
            except Exception as e:
                print(f"❌ Erreur vérif vidéo : {e}")

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
                        print(f"🗞️ Dernier post : {last_post}")
                        break
            except Exception as e:
                print(f"❌ Erreur extraction post : {e}")

            if debug:
                print("📄 Lignes de texte scrappées :")
                for l in lines:
                    print(f"→ {l}")

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
            print(f"⚠️ Erreur Facebook : {e}")
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 Capture d'erreur enregistrée : {screenshot_path}")
            return {}
        finally:
            browser.close()
