from playwright.sync_api import sync_playwright
from utils.logger import logger

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Accès à la page de login Facebook
    page.goto("https://www.facebook.com/login")
    logger.info("🔐 Connecte-toi manuellement dans le navigateur ouvert...")

    # Attente que tu sois sur la page d'accueil après login
    try:
        page.wait_for_url("https://www.facebook.com/", timeout=120000)
    except Exception:
        logger.warning("⚠️ Timeout : tu n'es pas resté(e) sur la page Facebook assez longtemps.")

    # Sauvegarde de l'état de session
    context.storage_state(path="cookie/fb_auth.json")
    logger.info("✅ Session Facebook sauvegardée dans cookie/fb_auth.json")

    browser.close()
