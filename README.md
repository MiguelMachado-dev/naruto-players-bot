# NarutoPlayers Bot

Bot automatizado para o jogo NarutoPlayers que gerencia caçadas e invasões automaticamente.

## Funcionalidades

- Login automático (com captcha resolvido por Gemini AI)
- Seleção automática de personagem
- Caçadas automáticas
- Processamento de invasões
- Sistema de reconhecimento de captcha para caçadas por imagem
- Sistema de reconhecimento de captcha para login por Gemini AI
- Sistema de estatísticas de caçadas
- Logs detalhados de execução

## Pré-requisitos

- Python 3.10.11 é recomendado
- pip (gerenciador de pacotes Python)
- Navegador Chromium (será instalado automaticamente pelo Playwright)
- Uma chave de API do Google Gemini (necessária para resolver o captcha de login)

## Instalação

1. Clone este repositório ou baixe os arquivos do bot

2. Crie um ambiente virtual Python (recomendado):
```bash
python -m venv npbot
```

3. Ative o ambiente virtual:
   - Windows:
   ```bash
   npbot\Scripts\activate
   ```
   - Linux/Mac:
   ```bash
   source npbot/bin/activate
   ```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Instale os navegadores necessários do Playwright:
```bash
playwright install chromium
```

## Configuração

1. Chave de API do Google Gemini:
   - Obtenha uma chave de API no Google AI Studio: https://aistudio.google.com/app/apikey

2. Arquivo .env:
   - Crie um arquivo chamado `.env` na raiz do projeto OU renomeie o existente `.env.example` para `.env`.
   - Adicione as seguintes variáveis ao arquivo .env, substituindo os valores pelos seus:
   ```bash
   NP_USER=seu_usuario
   NP_PASSWORD='sua_senha'
   GOOGLE_API_KEY=sua_chave_de_api_do_google
   ```

## Uso

1. Execute o bot:
```bash
python index.py
```

2. O bot iniciará a execução automática:
   - Realizará o login automático (resolvendo o captcha com Gemini AI)
   - Selecionará o personagem
   - Realizará caçadas
   - Verificará invasões disponíveis
   - Manterá logs em arquivos com timestamp
   - Salvará estatísticas em `bot_stats.json`

## Estrutura de Arquivos

```
├── index.py
├── bot/
│   ├── naruto_bot.py
│   ├── captcha_processor.py
│   ├── login_captcha_processor.py
│   └── utils.py
├── naruto.jpeg
├── sakura.jpeg
├── sasuke.jpeg
├── kakashi.jpeg
├── naruto_hashes.txt
├── sakura_hashes.txt
├── sasuke_hashes.txt
├── kakashi_hashes.txt
├── bot_stats.json
├── bot_log_[timestamp].log
├── config.py
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## Logs e Estatísticas

- Logs são salvos em arquivos com o formato `bot_log_YYYYMMDD_HHMMSS.log`
- Estatísticas são salvas em `bot_stats.json`
- Os logs incluem:
  - Identificação de personagens
  - Resultados de caçadas
  - Processamento de invasões
  - Erros e exceções

## Personalizações

Você pode ajustar vários parâmetros do bot:

1. Timeouts e delays:
   - Modifique os valores de `wait_for_timeout()` para ajustar os tempos de espera
   - Ajuste os `random.uniform()` para variar os tempos entre ações

2. Dimensões da janela:
   - Ajuste o viewport em:
   ```python
   viewport={'width': 1920, 'height': 1080}
   ```

3. Threshold de reconhecimento:
   - Modifique o valor `30` em `return best_match if min_total_distance <= 30 else None` para ajustar a precisão do reconhecimento de captcha

## Solução de Problemas

1. Erro no reconhecimento de captcha:
   - Verifique se as imagens dos personagens estão na pasta correta
   - Certifique-se que os nomes dos arquivos estão corretos e em minúsculo
   - Tente ajustar o threshold de reconhecimento

2. Erros de timeout:
   - Aumente os valores de timeout nas chamadas `wait_for_timeout()`
   - Verifique sua conexão com a internet

3. Falhas no login:
   - Certifique-se que as credenciais estão corretas
   - Verifique se o site está acessível
   - Verifique se a chave da API do Google Gemini está configurada corretamente no arquivo `.env`

## Avisos Importantes

- Use o bot de forma responsável
- Mantenha suas credenciais seguras
- Monitore a execução do bot regularmente
- Backup seus arquivos de estatísticas e logs

## Licença

Este projeto é para uso pessoal e educacional.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.