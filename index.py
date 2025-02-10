from playwright.sync_api import sync_playwright
from PIL import Image
import imagehash
import io
import logging
import os
import time
import re
from datetime import datetime
from typing import Dict, Optional, Tuple
import json
import random
import google.generativeai as genai
import dotenv

# Carrega variáveis de ambiente
dotenv.load_dotenv()

USER= os.getenv("USER")
PASSWORD= os.getenv("PASSWORD")

# Configuração do Google AI (Gemini)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("A chave API do Google (GOOGLE_API_KEY) não está configurada.")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-pro-exp-02-05')

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(f'bot_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

class CaptchaProcessor:  # Mantido do seu código original (para captcha de personagem)
    def __init__(self, characters: list):
        self.characters = characters
        self.reference_hashes = {}
        self._load_all_reference_hashes()

    def _load_all_reference_hashes(self) -> None:
        """Carrega todos os hashes de referência na inicialização"""
        for char in self.characters:
            try:
                self._load_or_create_hashes(char)
            except Exception as e:
                logging.error(f"Erro ao carregar hashes para {char}: {e}")

    def _load_or_create_hashes(self, char: str) -> None:
        """Carrega ou cria hashes para um personagem específico"""
        hash_file = f"{char.lower()}_hashes.txt"

        if os.path.exists(hash_file):
            self._load_hashes_from_file(char, hash_file)
        else:
            self._create_and_save_hashes(char)

    def _load_hashes_from_file(self, char: str, hash_file: str) -> None:
        """Carrega hashes de um arquivo"""
        with open(hash_file, "r") as f:
            lines = f.read().strip().split('\n')
            self.reference_hashes[char] = {
                'phash': imagehash.hex_to_hash(lines[0]),
                'ahash': imagehash.hex_to_hash(lines[1]),
                'dhash': imagehash.hex_to_hash(lines[2])
            }
        logging.info(f"Hashes de {char} carregados do arquivo.")

    def _create_and_save_hashes(self, char: str) -> None:
        """Cria e salva novos hashes para um personagem"""
        image_path = f"{char.lower()}.jpeg"
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Imagem de referência não encontrada: {image_path}")

        with open(image_path, "rb") as f:
            image_data = f.read()

        hashes = self._get_image_hashes(image_data)
        if not hashes:
            raise ValueError(f"Não foi possível gerar hashes para {char}")

        self.reference_hashes[char] = hashes
        self._save_hashes_to_file(char, hashes)

    def _save_hashes_to_file(self, char: str, hashes: Dict) -> None:
        """Salva hashes em um arquivo"""
        with open(f"{char.lower()}_hashes.txt", "w") as f:
            f.write(str(hashes['phash']) + '\n')
            f.write(str(hashes['ahash']) + '\n')
            f.write(str(hashes['dhash']) + '\n')
        logging.info(f"Hashes de {char} salvos em arquivo.")

    @staticmethod
    def _get_image_hashes(image_data: bytes) -> Optional[Dict]:
        """Calcula os hashes de uma imagem"""
        try:
            image = Image.open(io.BytesIO(image_data))
            return {
                'phash': imagehash.phash(image),
                'ahash': imagehash.average_hash(image),
                'dhash': imagehash.dhash(image)
            }
        except Exception as e:
            logging.exception("Erro ao calcular hashes da imagem:")
            return None

    def identify_character(self, page) -> Optional[str]:
        """Identifica um personagem baseado na imagem do captcha"""
        try:
            captcha_div = page.locator(".teste_img")
            captcha_image_buffer = captcha_div.screenshot(omit_background=True)
            captcha_hashes = self._get_image_hashes(captcha_image_buffer)

            if not captcha_hashes:
                return None

            return self._find_best_match(captcha_hashes)
        except Exception as e:
            logging.exception("Erro ao identificar personagem:")
            return None

    def _find_best_match(self, captcha_hashes: Dict) -> Optional[str]:
        """Encontra o melhor match entre os hashes de referência"""
        best_match = None
        min_total_distance = float('inf')

        for char, ref_hashes in self.reference_hashes.items():
            total_distance = sum(
                captcha_hashes[hash_type] - ref_hashes[hash_type]
                for hash_type in captcha_hashes
            )

            logging.debug(f"Distância total para {char}: {total_distance}")

            if total_distance < min_total_distance:
                min_total_distance = total_distance
                best_match = char

        return best_match if min_total_distance <= 30 else None
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
            response = model.generate_content([prompt, image])

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



class NarutoBot:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.character_to_id = {
            "Naruto": "teste_resp1",
            "Sakura": "teste_resp2",
            "Sasuke": "teste_resp3",
            "Kakashi": "teste_resp4"
        }
        self.captcha_processor = CaptchaProcessor(list(self.character_to_id.keys()))
        self.login_captcha_processor = LoginCaptchaProcessor()  # Instância do novo processador
        self.stats = self._load_stats()

    def _load_stats(self) -> Dict:
        """Carrega estatísticas do bot de um arquivo JSON"""
        try:
            with open('bot_stats.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'total_hunts': 0,
                'successful_hunts': 0,
                'failed_hunts': 0,
                'total_runtime': 0,
                'last_run': None
            }

    def _save_stats(self) -> None:
        """Salva estatísticas do bot em um arquivo JSON"""
        with open('bot_stats.json', 'w') as f:
            json.dump(self.stats, f, indent=4)

    def update_stats(self, success: bool) -> None:
        """Atualiza as estatísticas do bot"""
        self.stats['total_hunts'] += 1
        if success:
            self.stats['successful_hunts'] += 1
        else:
            self.stats['failed_hunts'] += 1
        self.stats['last_run'] = datetime.now().isoformat()
        self._save_stats()

    @staticmethod
    def get_remaining_time(page) -> int:
        """Extrai o tempo restante do elemento HTML do timer"""
        try:
            # Primeiro verifica se o elemento existe com um timeout curto
            if not page.locator("#relogio_contador").is_visible(timeout=2000):
                logging.info("Contador não encontrado na página")
                return 0

            # Se existir, pega o texto com timeout curto
            timer_text = page.locator("#relogio_contador").inner_text(timeout=2000)
            match = re.match(r"(\d{2}):(\d{2}):(\d{2})", timer_text)
            if match:
                hours, minutes, seconds = map(int, match.groups())
                return hours * 3600 + minutes * 60 + seconds
            return 0
        except Exception as e:
            logging.info("Sem tempo de penalidade para aguardar")
            return 0


    def wait_for_hunt_timer(self, page) -> None:
        """Espera o timer de caçada terminar com tempo aleatório adicional"""
        remaining_time = self.get_remaining_time(page)
        if remaining_time > 0:
            # Adiciona um tempo aleatório extra para parecer mais humano
            extra_time = random.randint(5, 30)
            total_wait = remaining_time + extra_time
            logging.info(f"Aguardando {total_wait} segundos (inclui {extra_time}s aleatórios)")
            time.sleep(total_wait)
            page.reload()
            page.wait_for_load_state()

    def run(self) -> None:
        """Executa o bot principal"""
        start_time = time.time()

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=False)  # Mantenha headless=False para depuração
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()

                self._login(page)
                self._select_character(page)

                while True:
                    try:
                        success = self._execute_hunt_cycle(page)
                        self.update_stats(success)
                        time.sleep(random.uniform(2, 5))  # Delay aleatório
                    except Exception as e:
                        logging.exception("Erro durante ciclo de caçada:")
                        time.sleep(60)

            except Exception as e:
                logging.exception("Erro crítico durante execução do bot:")
            finally:
                self.stats['total_runtime'] += time.time() - start_time
                self._save_stats()
                browser.close()


    def _login(self, page, attempts=0) -> None:
        """Realiza o login no site, usando o Gemini para o captcha."""
        if attempts >= 3:  # Limite de 3 tentativas (conforme sugerido anteriormente)
            raise RuntimeError("Falha ao resolver o captcha de login após múltiplas tentativas.")
        page.goto("https://www.narutoplayers.com.br/")

        # Resolve o captcha de login
        captcha_solution = self.login_captcha_processor.solve_captcha(page)

        if captcha_solution:
            page.locator('input[name="usuario"]').fill(self.username)
            page.locator('input[name="senha"]').fill(self.password)
            page.locator('input[name="codigo"]').fill(captcha_solution) #Preenche o campo do captcha
            page.locator('input[value="Login"]').click()
            page.wait_for_load_state() # Espere a página após o login

            #Verifica se o login foi bem-sucedido.
            if page.locator("#menu_personagem").is_visible():
              logging.info("Login bem-sucedido!")
            else:
              logging.error("Falha no login. Verifique as credenciais e o captcha.")
              #Poderia adicionar um mecanismo para tentar novamente, ou abortar.

        else:
            logging.error("Não foi possível resolver o captcha de login.")
            self._login(page, attempts + 1)
            return


    def _select_character(self, page) -> None:
        """Seleciona o personagem no slot 1"""
        page.locator('#corpo .selecao_char a[href="?p=selecionar&slot=1"]').click()
        page.wait_for_timeout(1000)
        page.locator('input[onclick="javascript:redirect(\'?p=selecionar&slot=1&confirma=ok\'); return false;"]').click()

    def _process_invasion(self, page) -> bool:
        """Processa a invasão após a caçada"""
        try:
            # Clica no menu de invasão
            page.locator('.menu_lateral li a[href="?p=invasao"]').click()
            page.wait_for_timeout(1000)

            # Verifica se está escrito "Atacar!"
            invasion_text = page.locator('#relogio_invasao').inner_text()
            if invasion_text.strip() == "Atacar!":
                logging.info("Invasor disponível para ataque!")

                # Processa o captcha como na caçada
                identified_character = self.captcha_processor.identify_character(page)
                if not identified_character:
                    logging.warning("Falha na identificação do personagem na invasão")
                    return False

                radio_button_id = self.character_to_id.get(identified_character)
                if not radio_button_id:
                    logging.error(f"ID não encontrado para o personagem na invasão: {identified_character}")
                    return False

                # Seleciona o personagem e ataca
                page.wait_for_selector(f"#{radio_button_id}", state="visible", timeout=60000)
                page.locator(f"#{radio_button_id}").check()
                page.locator('#relogio_invasao').click()

                logging.info("Ataque ao invasor realizado com sucesso!")
                return True
            else:
                logging.info("Invasor não está disponível para ataque no momento")
                return False

        except Exception as e:
            logging.exception("Erro durante o processamento da invasão:")
            return False

    def _execute_hunt_cycle(self, page) -> bool:
        """Executa um ciclo completo de caçada"""
        page.wait_for_timeout(random.uniform(1000, 2000))
        page.locator('.menu_lateral li a[href="?p=cacadas"]').click()
        page.wait_for_timeout(random.uniform(1000, 2000))

        self.wait_for_hunt_timer(page)

        page.locator('.aba_bg a[href="?p=cacadas&action=aleatoria"]').click()
        page.wait_for_timeout(random.uniform(1000, 2000))
        page.select_option('select[name="inimigo_aleatorio"]', "1")

        identified_character = self.captcha_processor.identify_character(page)

        if not identified_character:
            logging.warning("Falha na identificação do personagem")
            page.reload()
            return False

        radio_button_id = self.character_to_id.get(identified_character)
        if not radio_button_id:
            logging.error(f"ID não encontrado para o personagem: {identified_character}")
            return False

        try:
            page.wait_for_selector(f"#{radio_button_id}", state="visible", timeout=60000)
            page.locator(f"#{radio_button_id}").check()
            page.locator('input[value="Caçar"]').click()
            page.wait_for_timeout(random.uniform(1000, 2000))
            page.locator('input[value="Atacar"]').click()
            enemy_name = page.locator('#box_dir .char_dentro_h .linha_css2 .col_css2').inner_text()
            logging.info(f"Caçando {enemy_name}...")

            # Marca o início da penalidade
            penalty_start = time.time()

            self._process_invasion(page)

            # Calcula quanto tempo já se passou durante o processamento da invasão
            elapsed_time = time.time() - penalty_start
            remaining_penalty = max(300 - elapsed_time, 0)  # 300 segundos (5 minutos) menos o tempo gasto

            if remaining_penalty > 0:
                logging.info(f"Aguardando {remaining_penalty:.1f} segundos restantes de penalidade...")
                time.sleep(remaining_penalty)

            return True

        except Exception as e:
            logging.exception("Erro durante a execução da caçada:")
            return False

if __name__ == "__main__":
    bot = NarutoBot(username=USER, password=PASSWORD)
    bot.run()