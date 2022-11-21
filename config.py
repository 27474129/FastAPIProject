import os
from dotenv import load_dotenv


load_dotenv()


DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("HOST")
BASE_API_PREFIX = "/api/v1"
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
API_URL = "https://probe.fbrq.cloud/v1"
