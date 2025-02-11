import os
from dotenv import load_dotenv

load_dotenv()

USER = os.getenv("NP_USER")
PASSWORD = os.getenv("NP_PASSWORD")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("A chave API do Google (GOOGLE_API_KEY) não está configurada.")