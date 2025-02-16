import logging
import io
from typing import Optional
from PIL import Image
import google.generativeai as genai

class LoginCaptchaProcessor:
    """Processador para o captcha de login (alfanumérico)."""

    def solve_captcha(self, page) -> Optional[str]:
        """Resolve o captcha de login usando o Gemini."""
        try:
            captcha_element = page.locator("#captcha_img #img_captcha")

            # Se o elemento não existe, pode ser que a página não carregou corretamente
            if not captcha_element.is_visible():
                logging.error("Elemento do captcha de login não encontrado.")
                return None

            captcha_image_buffer = captcha_element.screenshot()
            image = Image.open(io.BytesIO(captcha_image_buffer))

            # Prompt preciso para o Gemini
            prompt = "Responda apenas com os 5 caracteres alfanuméricos do captcha, sem mais nenhuma palavra ou espaço."
            logging.info("Resolvendo captcha de login com Gemini...")
            response = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21').generate_content([prompt, image])

            if response and response.text:
                #Limpa a resposta: Remove espaços
                cleaned_response = response.text.replace(" ", "").strip()

                logging.info(f"Resposta bruta do Gemini (login): {response.text}")
                logging.info(f"Resposta limpa do Gemini (login): {cleaned_response}")

                #Valida o tamanho
                if len(cleaned_response) == 5:
                  return cleaned_response
                else:
                  logging.warning(f"Resposta do Gemini para o login não tem 5 caracteres: {cleaned_response}")
                  return None
            else:
                logging.warning("Gemini não retornou uma resposta válida para o login.")
                return None

        except Exception as e:
            logging.exception("Erro ao resolver captcha de login com Gemini:")
            return None