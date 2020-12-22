import os


DATABASE_HOST = os.getenv("DATABASE_HOST", "127.0.0.1:5432")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")
DATABASE_NAME = os.getenv("DATABASE_NAME", "trivia")

SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

CORS_HEADERS = "Content-Type"