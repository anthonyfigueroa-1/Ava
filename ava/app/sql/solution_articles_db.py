import psycopg, os, time, json

from app.logs import logs

db = os.environ["DB"]

def add_article_db(article) -> None:
    id = article.get("id")
    title = article.get("title")
    description = article.get("description")
    description_text = article.get("description_text")
    keywords = article.get("keywords")
    visibility = article.get("folder_visibility")

    now = int(time.time())
    last_synced = now

    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO solution_articles
                        (
                            id, title, description, description_text, keywords, visibility, last_synced
                            )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        """,
                        (id, title, description, description_text, keywords, visibility, last_synced))

def update_img_metadata(images, article_id):
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE solution_articles
                        SET img_metadata = %s
                        WHERE id = %s
                        """, 
                        (images, article_id))

def query_article(id):
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT row_to_json(t) 
                        FROM (
                            SELECT id, title, description_text, img_metadata
                            FROM solution_articles
                            WHERE id = %s
                            )
                        AS t
                        """,
                        (id,))
            article = cur.fetchone()

    if article:
        article = article[0]
        return article

def ai_query_articles_slim(keywords: list[str]) -> list[dict] | None:

    keywords = [f"%{keyword}%" for keyword in keywords]

    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        WITH kw as (
                            SELECT unnest(%s::text[]) as keyword
                            ),
                        cleaned as (
                            SELECT s.id,
                            s.title,
                            regexp_replace(s.description_text, E'[\\r\\n]+', ' ', 'g') as clean_desc,
                            s.keywords
                            FROM solution_articles s
                            ),
                        matches as (
                            SELECT c.*,
                            SUM(word_similarity(c.clean_desc, keyword)) as score
                            FROM cleaned c
                            LEFT JOIN LATERAL (
                                SELECT keyword FROM kw
                                WHERE c.clean_desc ILIKE keyword 
                                OR c.title ILIKE keyword
                                ) m ON TRUE
                            GROUP BY c.id, c.title, c.clean_desc, c.keywords
                            )
                            SELECT row_to_json(t)
                            FROM matches
                            AS t
                            WHERE score IS NOT null
                            ORDER BY score DESC,
                            COALESCE(score, 0) DESC
                            LIMIT 15
                        """,
                        (keywords,)
                        )
                        
            articles = cur.fetchall()

    if articles:
        return articles

def ai_query_articles_id(ids: list[int]) -> list[dict] | None:
    clause = " OR ".join(f"id = %s" for _ in ids)
    query = f"""SELECT row_to_json(t)
    FROM (
            SELECT id, title, description, keywords
            FROM solution_articles
            WHERE ({clause})
            )
    AS t"""

    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute(query, [*ids])
            articles = cur.fetchall()

    if articles:
        return articles
