from scraping.social_playwright import scrape_instagram_profile

if __name__ == "__main__":
        url = "https://www.instagram.com/airfrance/"
        result = scrape_instagram_profile(url)
        print(result)
