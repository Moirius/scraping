from scraping.social_playwright import scrape_facebook_page

url = "https://www.facebook.com/Roadside.Burger"  # remplace par une page valide
data = scrape_facebook_page(url, debug=True)
print(data)
