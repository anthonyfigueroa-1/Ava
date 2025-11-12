import psycopg, os, time

db = os.environ["DB"]

def add_article_db(article) -> None:
    id = article.get("id")
    title = article.get("title")
    description = article.get("description")
    description_text = article.get("description_text")
    keywords = article.get("keywords")
    folder_visibility = article.get("folder_visibility")

    now = int(time.time())
    last_synced = now

    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO solution_articles
                        (
                            id, title, description, description_text, keywords, folder_visibility, last_synced
                            )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING;
                        """,
                        (id, title, description, description_text, keywords, folder_visibility, last_synced))

def ai_query_articles_slim(keywords: list[str]) -> list[dict] | None:
    pass

def ai_query_articles_id(ids: list[int]) -> list[dict] | None:
    pass
