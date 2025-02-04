# gateway
A service for retrieval-augmented course recommendations at Stevens Institute of Technology.

### Prerequisites:
- Docker
- Python 3.12.7 or later

### Setup:
1. Create a virtual environment for the project and install the packages listed in requirements.txt
2. Create a `.env` file in the root of the project containing:
   ```
   API_TOKEN=YOUR_AZURE_OPENAI_TOKEN
   PG_CONN_STR="host=localhost port=5432 dbname=postgres user=postgres password=postgres"
   TOKENIZERS_PARALLELISM=false
   ```
4. Deploy the postgres container defined in src/vectordb.

### Use:
For local use, initialize a `CourseRecommender` with the academic year for the course listing you want to scrape; e.g. the year for the courses in the fall semester and the courses in the spring semester of the subsequent year:
```
# will use data from fall 2024 and spring 2025
recommender = CourseRecommender(2024)
```
The CourseRecommender object will handle the creation of a new table containing documents/embedding data for each course. However, before queries/recommendations can be made, we must first scrape and index each course from the catalog page that year.
```
# only needs to be run once for a given years catalog
recommender.index()
```
The database will be preserved as long as it's container is not deleted.
To make recommendations, we can simply call:
```
text = "Can you recommend me some cool courses involving machine learning?"
recommendation = recommender.recommend(text)
print(recommendation) # Response from ChatGPT in Markdown format...
```
Or to get recommendations from a RESTful api, run the FastAPI service defined in src/api and make a curl request as such:
```
curl -X POST "http://localhost:8000/recommend" \
     -H "Content-Type: application/json" \
     -d '{"question": "Can you recommend me some cool courses involving machine learning?"}'
```
### Todos:
- [ ] Potentially refactor database to include courses from all years,
- [ ] Add more API functionalities
