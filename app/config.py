import os
from dotenv import load_dotenv

#Load file .env
load_dotenv()

#API
COINGECKO_BASE_URL=os.getenv("COINGECKO_BASE_URL")

#Database
DB_CONFIG={
    "dbname":os.getenv("DB_NAME")
    ,"user":os.getenv("DB_USER")
    ,"password":os.getenv("DB_PASSWORD")
    ,"host":os.getenv("DB_HOST")
    ,"port":os.getenv("DB_PORT")
}