import requests
from bs4 import BeautifulSoup
import time
import random
from typing import Generator, Tuple


class CatalogScraper:
    """
    Scraper for Stevens Institute of Technology course catalog.

    Attributes:
        year (int): Specifies course listings for the fall semester of the given year
                    and the spring semester of the subsequent year.
    """
    BASE_URL = "https://stevens.smartcatalogiq.com"

    def __init__(self, year: int, delay_range: Tuple[int, int] = (1, 2)):
        self.year = year
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"}) 
        self.delay_range = delay_range

    def _polite_delay(self):
        """Adds a random delay between requests to avoid detection."""
        time.sleep(random.uniform(*self.delay_range))

    def get_courses(self) -> Generator[Tuple[str, str, str, str], None, None]:
        """
        Yields course descriptions, codes, names, and links from the catalog.

        Yields:
            Tuple[str, str, str, str]: A tuple containing the course description,
                                       code, name, and page link.
        Raises:
            requests.exceptions.RequestException: For network-related errors.
            ValueError: If the catalog structure is unexpected.
        """
        yearly_listing = f"{self.BASE_URL}/en/{self.year}-{self.year + 1}/academic-catalog/courses/"

        try:
            response = self.session.get(yearly_listing)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Failed to fetch the catalog page: {e}")

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main')

        if not main_div:
            raise ValueError("Catalog structure has changed. 'main' div not found.")

        course_links = main_div.find_all('li')

        for li in course_links:
            a_tag = li.find('a')
            if not a_tag or not a_tag.get('href'):
                continue

            href = a_tag['href']
            course_page = f"{self.BASE_URL}{href}"
            course_code = (a_tag.find('span').text.strip()
                           if a_tag.find('span') else None)
            course_name = a_tag.text.strip().replace(course_code or '', '').strip()

            if not course_code:
                continue

            # Polite scraping
            self._polite_delay()

            try:
                course_response = self.session.get(course_page)
                course_response.raise_for_status()
            except requests.exceptions.RequestException:
                continue  # Skip failed requests

            course_soup = BeautifulSoup(course_response.content, 'html.parser')
            course_main_div = course_soup.find('div', id='main')

            if not course_main_div:
                continue

            desc_div = course_main_div.find('div', class_='desc')
            course_desc = desc_div.text.strip() if desc_div else "No description available."

            yield course_desc, course_code, course_name, course_page