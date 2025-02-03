import requests
from bs4 import BeautifulSoup

class CatalogScraper:
    '''
    Class for catalog scraping.

    @member year: specifies course listing for the fall semester of the given
    year and the spring semester of the subsequent year.
    '''
    def __init__(self, year: int):
        self.year: int = year
        
    def get_courses(self, debug=False, debugLimit=211) -> tuple[str, str, str, str]:
        '''
        Crawls the Stevens Institute of Technology catalog page and yields
        tuples containing course descriptions, codes, names, and links.
        
        @param debug: toggles printing of the urls being scraped.
        @yield course: tuple[str, str, str]
        @raise StopIteration: once there are no more courses to list.
        @raise requests.exceptions.Error: if the request is bad.
        @raise NotImplementedError: if there is not a div with the id of 'main'.
        '''
        base = "https://stevens.smartcatalogiq.com"
        yearly_listing = f"{base}/en/{self.year}-{self.year+1}/academic-catalog/courses/"

        response = requests.get(yearly_listing)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main')

        if not main_div:
            raise NotImplementedError

        course_links = main_div.find_all('li')

        if debug:
            count = 0

        for li in course_links:

            if debug:
                count += 1
                if count >= debugLimit:
                    break

            a_tag = li.find('a')
            if a_tag and a_tag.get('href'):
                href = a_tag['href']
                span_tag = a_tag.find('span')
                course_code = span_tag.text.strip() if span_tag else None
                course_name = a_tag.text.strip()
                
                if not course_code:
                    continue
                
                course_name = course_name.replace(course_code, '').strip()
                course_page = base + href

                try:
                    if debug:
                        print(f"Fetching: {course_page}")
                    course_response = requests.get(course_page)
                    course_response.raise_for_status()
                except Exception as ex:
                    if debug:
                        print(f"Failed to fetch {course_page}: {ex}")
                    continue

                course_soup = BeautifulSoup(course_response.content, 'html.parser')
                course_main_div = course_soup.find('div', id='main')

                if not course_main_div:
                    continue
                
                desc_div = course_main_div.find('div', class_='desc')
                course_desc = desc_div.text.strip()

                yield course_desc, course_code, course_name, course_page
