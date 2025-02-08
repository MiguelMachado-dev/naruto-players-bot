# NarutoPlayers Bot

Bot automatizado para o jogo NarutoPlayers que gerencia caçadas e invasões automaticamente.

## Funcionalidades

- Login automático (com captcha manual)
- Seleção automática de personagem
- Caçadas automáticas
- Processamento de invasões
- Sistema de reconhecimento de captcha por imagem
- Sistema de estatísticas de caçadas
- Logs detalhados de execução

## Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Navegador Chromium (será instalado automaticamente pelo Playwright)

## Instalação

1. Clone este repositório ou baixe os arquivos do bot

2. Crie um ambiente virtual Python (recomendado):
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
   - Windows:
   ```bash
   venv\Scripts\activate
   ```
   - Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. Instale as dependências:
```bash
pip install playwright pillow imagehash
```

5. Instale os navegadores necessários do Playwright:
```bash
playwright install
```

## Configuração

1. Imagens de referência:
   - Você precisa ter imagens JPEG dos personagens para o reconhecimento do captcha
   - Nomeie as imagens em minúsculo: `naruto.jpeg`, `sakura.jpeg`, `sasuke.jpeg`, `kakashi.jpeg`
   - Coloque as imagens na mesma pasta do script

2. Configurações do bot:
   - Abra o arquivo Python e modifique as seguintes linhas com suas credenciais:
   ```python
   if __name__ == "__main__":
       bot = NarutoBot(username="seu_usuario", password="sua_senha")
       bot.run()
   ```

## Uso

1. Execute o bot:
```bash
python nome_do_script.py
```

2. Quando solicitado, preencha manualmente o captcha de login e pressione Enter no terminal

3. O bot começará a executar automaticamente:
   - Realizará caçadas
   - Verificará invasões disponíveis
   - Manterá logs em arquivos com timestamp
   - Salvará estatísticas em `bot_stats.json`

## Estrutura de Arquivos

```
├── nome_do_script.py
├── naruto.jpeg
├── sakura.jpeg
├── sasuke.jpeg
├── kakashi.jpeg
├── bot_stats.json
└── bot_log_[timestamp].log
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

## Avisos Importantes

- Use o bot de forma responsável
- Mantenha suas credenciais seguras
- Monitore a execução do bot regularmente
- Backup seus arquivos de estatísticas e logs

## Licença

Este projeto é para uso pessoal e educacional.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.