import requests, os, re
from requests.auth import HTTPBasicAuth

from app.sql.solution_articles_db import add_article_db 
from app.logs import logs

key = os.environ["FSKEY"]

def search_articles(keyword):
    keyword = re.sub(r" ", "%20", keyword) #allows keyword to be processed via the url if the keyword happens to have spaces

    url = f"https://eastwest.freshservice.com/api/v2/solutions/articles/search?search_term={keyword}&per_page=15"

    counter = 1

    while True:
        try:
            response = requests.get(url, auth=HTTPBasicAuth(key, 'X'), timeout=(20,20))

            if response.status_code != 200:
                logs(f"Failed to get solutions articles from FS")
                logs(f"With error code of {response.status_code}")

            else:
                articles = response.json()["articles"] 
                for article in articles:
                    add_article_db(article)
                return articles

        except requests.exceptions.Timeout:
            pass

        if counter <= 3:
            break
        else:
            counter +=1

def get_some_articles(ids):
    articles = []

    for id in ids:
        url = f"https://eastwest.freshservice.com/api/v2/solutions/articles/{id}"

        counter = 1

        while True:
            try:
                response = requests.get(url, auth=HTTPBasicAuth(key, 'X'), timeout=(20,20))

                if response.status_code != 200:
                    logs(f"Failed to get solutions article {id} from FS")
                    logs(f"With error code of {response.status_code}")

                else:
                    article = response.json()["article"]
                    articles.append(article)
                    break

            except requests.exceptions.Timeout:
                pass

            if counter <= 3:
                break
            else:
                counter +=1

    return articles
