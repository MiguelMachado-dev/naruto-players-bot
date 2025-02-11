import logging
import os
from datetime import datetime
import google.generativeai as genai
from playwright.sync_api import sync_playwright
import config
from bot.naruto_bot import NarutoBot

# Configuração do Google AI (Gemini)
genai.configure(api_key=config.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/bot_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    bot = NarutoBot(username=config.USER, password=config.PASSWORD)
    bot.run()