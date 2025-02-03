from src.crawler.scraper import CatalogScraper

scraper = CatalogScraper(2024)
courses = scraper.get_courses(debug=True)
print(next(courses))