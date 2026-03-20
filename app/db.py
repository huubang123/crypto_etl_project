import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()  

def get_engine():
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_name = os.getenv("DB_NAME")
    db_password = os.getenv("DB_PASSWORD")

    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    engine = create_engine(db_url)
    return engine