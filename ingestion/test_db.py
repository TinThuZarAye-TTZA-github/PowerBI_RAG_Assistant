import psycopg
from database_connection import get_connection

conn = psycopg.connect(
    host="localhost",
    port = 5434,
    dbname = "powerbi_rag",
    user = "raguser",
    password = ""
)
print("Connected to Postgres")
conn.close()