from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres"

engine = create_engine(DATABASE_URL)