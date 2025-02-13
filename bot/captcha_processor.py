import logging
import os
import io
from typing import Dict, Optional
from PIL import Image
import imagehash

class CaptchaProcessor:
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
            captcha_div.wait_for(state='visible', timeout=60000)
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