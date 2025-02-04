from src.crawler.scraper import CatalogScraper

scraper = CatalogScraper(2024)
courses = scraper.get_courses()

for i in range(21):
    print(next(courses)[1])