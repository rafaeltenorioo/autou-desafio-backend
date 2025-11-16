# API Assistente de emails - Desafio AutoU

Esta é a API de backend (Python/Flask) para o desafio técnico da AutoU.

Este servidor recebe o texto (via input direto ou upload de arquivo .txt/.pdf), o processa, e o envia para a API do Google Gemini para classificação e geração de resposta em nome da "Nexus Finanças".

* **Link da Aplicação (Frontend):** `https://autou-desafio-frontend.vercel.app/`
* **Link do Repositório (Frontend):** `https://github.com/rafaeltenorioo/autou-desafio-frontend`

---

## 🛠️ Stack de Tecnologia

* **Python 3**
* **Flask:** Para criar o servidor e a rota de API.
* **Gunicorn:** Para rodar o servidor em produção (no deploy).
* **Google Gemini (API):** Para classificação e geração de resposta.
* **PyPDF2:** Para extrair texto de arquivos .pdf.
* **Render.com:** Para o deploy em nuvem.

---

## 🚀 Como Executar Localmente

Siga estas instruções para rodar o servidor em sua máquina local:

### 1. Clonar o Repositório
git clone https://github.com/rafaeltenorioo/autou-desafio-backend.git cd autou-desafio-backend


### 2. Criar e Ativar Ambiente Virtual
#### Criar o venv:

python -m venv venv

#### Ativar no Windows (PowerShell):

.\venv\Scripts\activate

#### Ativar no Mac/Linux:

source venv/bin/activate


### 3. Instalar Dependências
O arquivo `requirements.txt` está incluído no projeto.

pip install -r requirements.txt

### 4. Configurar Chave de API (Obrigatório)
Este projeto usa a API do Google Gemini. A chave **não** está no código por segurança.

1.  Obtenha sua chave no [Google AI Studio](https://makers.google.com/).
2.  Defina a chave como uma variável de ambiente:

    *No Windows (PowerShell):*
    ```
    $env:GEMINI_API_KEY = "SUA_CHAVE_AIza..."
    ```
    *No Mac/Linux:*
    ```
    export GEMINI_API_KEY="SUA_CHAVE_AIza..."
    ```

### 5. Rodar o Servidor
python app.py
O servidor estará rodando em `http://127.0.0.1:5000`.

---

## 🧠 Decisões Técnicas (Sobre NLP)

O desafio mencionava técnicas de NLP como *stemming* e *stop words*.

Optei por uma abordagem mais moderna usando um **LLM (Google Gemini)**. Este modelo não requer pré-processamento manual (remover stop-words, etc.), pois ele analisa o contexto e o sentimento da frase *completa*, o que resulta em uma classificação e resposta mais precisas e naturais. O "treinamento" da IA foi feito através de um *system prompt* robusto, que define a personalidade ("Nexus Finanças") e as regras de negócio.
