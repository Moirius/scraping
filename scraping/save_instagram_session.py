from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Accès à la page de login Instagram
    page.goto("https://www.instagram.com/accounts/login/")
    print("🔐 Connecte-toi manuellement dans le navigateur lancé...")

    # Attendre que tu sois connecté
    page.wait_for_url("https://www.instagram.com/", timeout=120000)  # 2 minutes max

    # Sauvegarde du contexte une fois connecté
    context.storage_state(path="cookie/ig_auth.json")
    print("✅ Session Instagram sauvegardée dans cookie/ig_auth.json")
    browser.close()
