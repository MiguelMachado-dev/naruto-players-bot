import logging
import time
import random
from datetime import datetime
from typing import Dict
import re
from playwright.sync_api import sync_playwright
from .captcha_processor import CaptchaProcessor
from .login_captcha_processor import LoginCaptchaProcessor
from .utils import load_stats, save_stats

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
        self.login_captcha_processor = LoginCaptchaProcessor()
        self.stats = load_stats()
        logging.info("NarutoBot inicializado.")

        # Adiciona a escolha do tipo de caçada no início
        self.hunt_type = self._choose_hunt_type()

    def _choose_hunt_type(self) -> int:
        """Permite ao usuário escolher o tipo de caçada."""
        while True:
            print("Escolha o tipo de caçada:")
            print("1 - Caçada aleatória")
            print("2 - Caçada por tempo")
            choice = input("Digite 1 ou 2: ")
            if choice in ("1", "2"):
                return int(choice)
            else:
                print("Opção inválida. Digite 1 ou 2.")

    def _load_stats(self) -> Dict:
        """Carrega estatísticas do bot de um arquivo JSON"""
        return load_stats()

    def _save_stats(self) -> None:
        """Salva estatísticas do bot em um arquivo JSON"""
        save_stats(self.stats)

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

    @staticmethod
    def get_remaining_invasion_time(page) -> int:
        """Extrai o tempo restante do elemento HTML do timer de invasão"""
        try:
            # Primeiro verifica se o elemento existe com um timeout curto
            if not page.locator("#relogio_invasao").is_visible(timeout=2000):
                logging.info("Contador de invasão não encontrado na página")
                return 0

            # Se existir, pega o texto com timeout curto
            timer_text = page.locator("#relogio_invasao").inner_text(timeout=2000)
            match = re.match(r"(\d{2}):(\d{2}):(\d{2})", timer_text)
            if match:
                hours, minutes, seconds = map(int, match.groups())
                return hours * 3600 + minutes * 60 + seconds
            return 0
        except Exception as e:
            logging.info("Sem tempo de invasão para aguardar")
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
        logging.info("Iniciando a execução do bot.")

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)  # Mantenha headless=False para depuração
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()

                self._login(page)
                self._select_character(page)

                while True:
                    try:
                        if self.hunt_type == 1:
                            success = self._execute_hunt_cycle(page)
                        elif self.hunt_type == 2:
                            success = self._execute_timed_hunt_cycle(page)
                        else:
                            raise ValueError("Tipo de caçada inválido.")
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
        logging.info("Acessando a página de login.")
        page.goto("https://www.narutoplayers.com.br/")
        page.wait_for_load_state()

        # Resolve o captcha de login
        captcha_solution = self.login_captcha_processor.solve_captcha(page)

        if captcha_solution:
            page.locator('input[name="usuario"]').fill(self.username)
            page.locator('input[name="senha"]').fill(self.password)
            page.locator('input[name="codigo"]').fill(captcha_solution) #Preenche o campo do captcha
            page.locator('input[value="Login"]').click()
            page.wait_for_load_state() # Espere a página após o login

            #Verifica se o login foi bem-sucedido.
            if page.locator('#corpo .selecao_char a[href="?p=selecionar&slot=1"]').is_visible():
                logging.info("Login bem-sucedido!")
            else:
                logging.error("Falha no login. Verifique as credenciais e o captcha.")
                self._login(page, attempts + 1)
                return

        else:
            logging.error("Não foi possível resolver o captcha de login.")
            self._login(page, attempts + 1)
            return


    def _select_character(self, page) -> None:
        """Seleciona o personagem no slot 1"""
        logging.info("Selecionando personagem no slot 1.")
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
                # Verifica se o ataque foi bem-sucedido, caso a url possua &aviso=5 é porque o ataque deu errado
                if "&aviso=5" in page.url:
                    logging.error("Erro ao atacar o invasor.")
                    # Loga o erro da pagina
                    error_text = page.locator('#error').inner_text()
                    logging.error(error_text)
                    # Se error_text conter a seguinte frase "25 pontos de HP", va para status e recupe o HP.
                    if "25 pontos de HP" in error_text:
                        page.locator('.menu_lateral li a[href="?p=status"]').click()
                        page.wait_for_load_state()
                        hp_text = page.locator('#hp_baixo .hp_xp').inner_text()
                        current_hp = int(hp_text.split("/")[0].strip())
                        max_hp = int(hp_text.split("/")[1].strip())
                        if current_hp < max_hp / 2:
                            logging.info("HP baixo, curando...")
                            use_link = page.locator('a').filter(has_text="Usar").nth(0)
                            if use_link:
                                use_link.click()
                            else:
                                logging.error("Link 'Usar' não encontrado.")
                                return False
                        else:
                            logging.info("HP atual: %d/%d, não é necessário curar.", current_hp, max_hp)
                    return False

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
        page.wait_for_selector('.menu_lateral li a[href="?p=cacadas"]', state='visible', timeout=30000)
        page.locator('.menu_lateral li a[href="?p=cacadas"]').click()
        page.wait_for_timeout(random.uniform(1000, 2000))
        logging.info("Iniciando caçada...")

        self.wait_for_hunt_timer(page)

        page.locator('.aba_bg a[href="?p=cacadas&action=aleatoria"]').click()
        logging.info("Selecionando inimigo aleatório...")
        page.wait_for_timeout(random.uniform(1000, 2000))
        page.select_option('select[name="inimigo_aleatorio"]', "1")
        logging.info("Inimigo equivalente selecionado!")

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
            try:
                page.wait_for_selector('input[value="Atacar"]', timeout=30000)
                page.locator('input[value="Atacar"]').click()
            except Exception as e:
                logging.error(f"Falha ao clicar no botão 'Atacar': {e}")
                return False
            enemy_name = page.locator('#box_dir .char_dentro_h .linha_css2 .col_css2').inner_text()
            logging.info(f"Caçando {enemy_name}...")
            first_element = page.locator("#corpo_col_dir .linha_css_memo.center").nth(0)
            if first_element:
                battle_result = first_element.inner_text()
                logging.info(battle_result)
            else:
                logging.info("Resultado da batalha não encontrado")

            # Marca o início da penalidade
            penalty_start = time.time()

            invasion_successful = self._process_invasion(page)

            # Se a invasão não foi bem-sucedida, vá para a página de status
            if not invasion_successful:
                logging.info("Invasão não disponível, indo para a página de status.")
                page.locator('.menu_lateral li a[href="?p=status"]').click()
                # Espere a pagina carregar
                page.wait_for_load_state()
                # Cheque o hp do personagem
                hp_text = page.locator('#hp_baixo .hp_xp').inner_text()
                # Se estiver abaixo de 50%, vamos curar.
                current_hp = int(hp_text.split("/")[0].strip())
                max_hp = int(hp_text.split("/")[1].strip())
                if current_hp < max_hp / 2:
                    logging.info("HP baixo, curando...")
                    use_link = page.locator('a').filter(has_text="Usar").nth(0)
                    if use_link:
                        use_link.click()
                    else:
                        logging.error("Link 'Usar' não encontrado.")
                        return False
                    page.wait_for_timeout(2000)
                else:
                    logging.info("HP atual: %d/%d, não é necessário curar.", current_hp, max_hp)

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

    def _execute_timed_hunt_cycle(self, page) -> bool:
        """Executa um caça por tempo"""
        page.wait_for_timeout(random.uniform(1000, 2000))
        page.wait_for_selector('.menu_lateral li a[href="?p=cacadas"]', state='visible', timeout=30000)
        page.locator('.menu_lateral li a[href="?p=cacadas"]').click()
        page.wait_for_timeout(random.uniform(1000, 2000))
        logging.info("Iniciando caçada...")

        self.wait_for_hunt_timer(page)

        page.locator('.aba_bg a[href="?p=cacadas&action=tempo"]').click()
        logging.info("Selecionando tempo de caça de 5 minutos...")

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

            # Marca o início da penalidade
            penalty_start = time.time()

            invasion_successful = self._process_invasion(page)

            # Se a invasão não foi bem-sucedida, vá para a página de status
            if not invasion_successful:
                logging.info("Invasão não disponível.")

            # Calcula quanto tempo já se passou durante o processamento da invasão
            elapsed_time = time.time() - penalty_start
            remaining_penalty = max(300 - elapsed_time, 0)  # 300 segundos (5 minutos) menos o tempo gasto

            if remaining_penalty > 0:
                logging.info(f"Aguardando {remaining_penalty:.1f} segundos restantes de penalidade...")
                time.sleep(remaining_penalty)

            page.wait_for_selector('.menu_lateral li a[href="?p=cacadas"]', state='visible', timeout=30000)
            page.locator('.menu_lateral li a[href="?p=cacadas"]').click()
            page.wait_for_load_state()

            try:
                page.locator('#form_cacadas #receber_m img').click()
                logging.info("Recebendo recompensa...")
                # Loga a recompença recebida
                reward_text = page.locator('#relogio_cacadas .cacada_recompensa.c_reco_alt').inner_text()
                logging.info(reward_text)
                page.wait_for_timeout(random.uniform(1000, 2000))
            except Exception as e:
                logging.error(f"Falha ao clicar no botão 'Receber': {e}")
                return False

            return True

        except Exception as e:
            logging.exception("Erro durante a execução da caçada:")
            return False