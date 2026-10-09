import os
import psycopg
from pgvector.psycopg import register_vector

def get_connection ():
    conn = psycopg.connect(
        host = os.getenv("DB_HOST", "localhost"),
        port = int(os.getenv("DB_PORT", "5434")),
        dbname = os.getenv("DB_NAME", "powerbi_rag"),
        user = os.getenv("DB_USER", "raguser"),
        password = os.getenv("DB_PASSWORD")
    )
    register_vector(conn)
    return conn