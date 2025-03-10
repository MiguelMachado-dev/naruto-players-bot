import logging
import os
from datetime import datetime
import google.generativeai as genai
import config
from bot.naruto_bot import NarutoBot

# Configuração do Google AI (Gemini)
genai.configure(api_key=config.GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    bot = NarutoBot(username=config.USER, password=config.PASSWORD)
    bot.run()