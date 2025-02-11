import json
import logging

def load_stats():
    """Carrega estatísticas do bot de um arquivo JSON"""
    try:
        with open('bot_stats.json', 'r') as f:
            logging.info('Carregando estatísticas do bot...')
            return json.load(f)
    except FileNotFoundError:
        return {
            'total_hunts': 0,
            'successful_hunts': 0,
            'failed_hunts': 0,
            'total_runtime': 0,
            'last_run': None
        }

def save_stats(stats):
    """Salva estatísticas do bot em um arquivo JSON"""
    with open('bot_stats.json', 'w') as f:
        logging.info('Salvando estatísticas do bot...')
        json.dump(stats, f, indent=4)