from scraping.social_playwright import scrape_facebook_page

if __name__ == "__main__":
    # 🔗 Remplace cette URL par celle d'une vraie page Facebook publique
    url = "https://www.facebook.com/bretone.rennes"  # Exemple

    print(f"🔍 Scraping de la page Facebook : {url}")
    stats = scrape_facebook_page(url)

    print("📊 Résultats Facebook :")
    print(stats)
