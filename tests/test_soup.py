import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    base = "https://stevens.smartcatalogiq.com"

    listings_url = f"{base}/en/2024-2025/academic-catalog/courses/"

    # Extract (href, course_code, course_name) tuples
    courses = []

    response = requests.get(listings_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main')
        if main_div:
            course_links = main_div.find_all('li')
            for li in course_links:
                a_tag = li.find('a')
                if a_tag and a_tag.get('href'):
                    href = a_tag['href']
                    span_tag = a_tag.find('span')
                    course_code = span_tag.text.strip() if span_tag else None
                    course_name = a_tag.text.strip()
                    if course_code:
                        course_name = course_name.replace(course_code, '').strip()
                    courses.append((href, course_code, course_name))
                break

        else:
            print("Couldn't find the main div.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

    course_url, course_code, course_name = courses[0]

    print(course_code)
    print(course_name)

    course_page_url = base + course_url

    response = requests.get(course_page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        main_div = soup.find('div', id='main')
        course_desc = main_div.find('div', class_='desc')
        if course_desc:
            print(course_desc.text.strip())
        
        # course_credits = main_div.find('div', class_='credits')
        # if course_credits:
        #     print(course_credits.text.strip())
        # course_prereqs = main_div.find('div', class_='sc_prereqs')
        # if course_prereqs:
        #     print(course_prereqs.text.replace("\t", "").replace("\n", "").strip())
        # course_coreqs = main_div.find('div', class_='sc_coreqs')
        # if course_coreqs:
        #     if course_coreqs.text:
        #         print(course_coreqs.text.replace("\t", "").replace("\n", "").strip())

