import psycopg
from database_connection import get_connection

#Information about the microsoft article
title = "Understand star schema and the importance for Power BI"
url = "https://learn.microsoft.com/en-us/power-bi/guidance/star-schema"

# connect to postgreSQL
with get_connection() as conn:
    with conn.cursor() as cursor:

        #Insert the article into the document table
        cursor.execute(
            """
            INSERT INTO documents (title, source_url)
            VALUES (%s, %s)
            ON CONFLICT(source_url)
            DO UPDATE SET title = EXCLUDED.title
            RETURNING id
            """,
            (title, url)
        )

        document_id = cursor.fetchone()[0]
        print("Saved Document ID : ", document_id)

