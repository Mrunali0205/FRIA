from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),  # handles @ safely
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)

print("DATABASE_URL =", DATABASE_URL)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("DB RESULT =", result.scalar())
