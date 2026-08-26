import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    db_url = "postgresql+psycopg://postgres:postgres@localhost:5432/promptsentinel"

# Extract connection details
import urllib.parse
parsed = urllib.parse.urlparse(db_url)
user = parsed.username
password = parsed.password
host = parsed.hostname
port = parsed.port

conninfo = f"user={user} password={password} host={host} port={port} dbname=postgres"

try:
    with psycopg.connect(conninfo, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = 'promptsentinel_test'")
            if not cur.fetchone():
                cur.execute("CREATE DATABASE promptsentinel_test")
                print("Created promptsentinel_test database")
            else:
                print("promptsentinel_test already exists")
except Exception as e:
    print(f"Error: {e}")
