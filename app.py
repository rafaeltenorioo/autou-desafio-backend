import os # Para ler a variável de ambiente
import json # Para converter a resposta da IA
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

import io # Para ler o arquivo da memória
import PyPDF2

# Inicialização
# Flask está criando app, '__name__' é uma variável padrão
app = Flask(__name__)

# Aplicando o 'crachá' de segurança em toda a aplicação
CORS(app)

try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    genai.configure(api_key=GEMINI_API_KEY)

except Exception as e:
    print(f"Erro ao configurar a API do Gemini: {e}")
    # Se falhar na configuração, avisamos e saímos
    raise ValueError("Chave de API do Google (GEMINI_API_KEY) não encontrada ou inválida. Defina a variável de ambiente.")

def get_ai_analysis(email_content):
    """
    Usa a API do Gemini (Flash) para classificar E gerar uma resposta, forçando a saída em JSON.
    """

    system_prompt = """
    Você é  o assistente de IA de triagem de emails da Nexus Finanças.
    Sua tarefa é ler um email e executar 4 funções com precisão cirúrgica, como um especialista do setor financeiro:

    1.  **Classificar o Tópico:** Classifique o email rigorosamente como "Produtivo" ou "Improdutivo".
        * **Produtivo:** Requer uma ação da equipe Nexus. Isso inclui:
            * Solicitações (suporte, status de ticket, faturas).
            * Dúvidas (sobre serviços, taxas, plataforma).
            * Críticas ou Reclamações (tratar com urgência e empatia).
            * Envio de Documentos (confirmar recebimento).
        * **Improdutivo:** Não requer ação da equipe. Isso inclui:
            * Elogios ou Agradecimentos.
            * Mensagens de saudação (Feliz Natal, bom fim de semana).
            * Spam ou marketing não solicitado.
            * Perguntas fora do escopo.

    2.  **Detectar o Idioma:** Detecte automaticamente o idioma principal (Português, Inglês ou Espanhol).

    3.  **Sugerir Resposta (A Ação Principal):**
        * **SEMPRE** responda no mesmo idioma detectado.
        * **SEMPRE** seja cortês, profissional e assine como "Equipe Nexus Finanças".
        * **Para Críticas (Produtivo):** Responda com empatia, peça desculpas pelo problema e garanta que a equipe técnica/responsável já foi acionada para análise prioritária.
        * **Para Dúvidas (Produtivo):** Responda confirmando o recebimento da dúvida e informe que um especialista no assunto responderá em breve.
        * **Para Elogios (Improdutivo):** Agradeça calorosamente pelo feedback em nome da Nexus Finanças.
        * **Para Felicitações (Improdutivo):** Agradeça e retribua a felicitação (ex: "A equipe Nexus Finanças também lhe deseja...").
        * **Para Fora de Escopo (Improdutivo):** Se o email pedir algo totalmente fora do setor financeiro (ex: livros de filosofia, receitas, etc.), recuse educadamente, informando: "Nossa especialidade na Nexus Finanças é o setor financeiro. Não podemos ajudar com esta solicitação específica."

    4.  **Formatar a Saída:** Responda APENAS em formato JSON. A estrutura deve ser rigorosamente esta:
        {"categoria": "...", "resposta_sugerida": "..."}
    """

    # "Aqui definimos o "truque": queremos que a resposta seja JSON."
    generation_config = {
        "response_mime_type": "application/json",
    }

    # "Aqui criamos o 'Especialista' (Modelo Gemini 1.5 Flash) com a regra do JSON."
    # O "flash" é o modelo mais rápido, ideal para apps web.
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config=generation_config
    )
    try:
        # "Aqui fazemos a 'ligação' com o 'manual' e o 'email'."
        # O [system_prompt, email_content] é a conversa que enviamos.
        response = model.generate_content([system_prompt, email_content])
        
        # "A API já nos devolve a resposta em JSON, então só precisamos carregar o texto."
        # A resposta da API já é um objeto JSON
        ai_result_dict = json.loads(response.text)
        
        # Retorna o DICIONÁRIO (objeto) pronto
        return ai_result_dict

    except Exception as e:
        print(f"Erro na análise da IA (Gemini): {e}")
        return {
            "categoria": "Erro de IA", 
            "resposta_sugerida": f"Não foi possível processar o email com a IA (Gemini). Erro: {e}"
        }


# Cria uma rota com tal endereço que só aceita entregas 'POST'
@app.route('/process-email', methods=['POST'])
def handle_email():

    # Criando variável vazia p/ guardar o texto final
    email_content = ""

    # React mandou algo na etiqueta 'file'? 
    if 'file' in request.files:
        file_from_user = request.files['file']

        # Que tipo de arquivo ?
        if file_from_user.filename.endswith('.pdf'):
            try:
                # io.BytesIO carrega o arquivo na memória, pois PyPDF2 somente lê bytes.
                pdf_in_memory = io.BytesIO(file_from_user.read())

                pdf_reader = PyPDF2.PdfReader(pdf_in_memory)

                # Juntando o texto de todas as páginas
                text_list = []
                for page in pdf_reader.pages:
                    text_list.append(page.extract_text()) 
                
                email_content = " ".join(text_list)

            except Exception as e:
                print(f"Erro ao ler PDF: {e}")
                
                # Avisa ao Front que o pdf falhou
                return jsonify({"error": "Falha ao ler o arquivo PDF. Está corrompido?"}), 500
            
        elif file_from_user.filename.endswith('.txt'):
            try:
                # Lê e transforma de bytes p/ texto
                email_content = file_from_user.read().decode('utf-8')
            except Exception as e:
                print(f"Erro ao ler TXT: {e}")
                return jsonify({"error": "Falha ao ler o arquivo TXT."}), 500
        
        else:
            # "Se não for .txt nem .pdf, recuse."
            return jsonify({"error": "Formato de arquivo não suportado. Envie .txt ou .pdf"}), 400
        
    # Se ñ veio arquivo, veio texto do textarea?
    elif 'emailText' in request.form:
        email_content = request.form['emailText']

    if not email_content:
        return jsonify({"error": "Nenhum texto ou arquivo válido fornecido"}), 400

    # "Avisa no terminal que o pedido chegou"
    print(f'Recebido para processar (primeiros 50 chars): {email_content[:50]}...')

    # IA (chamando a função com o email)
    ai_result_dict = get_ai_analysis(email_content)
   
    # ! Resposta 
    # Empacota o objeto Python vindo da IA como um JSON para o front-end
    return jsonify(ai_result_dict)

# Rodando o servidor
# Se alguém rodou esse arquivo (app.py) sem importa-lo...
if __name__ == '__main__':

    # Abre o app na porta 5000, já que o React geralmente usa a 3000. debug=True faz com que o servidor reinicie ao salvar o arquivo
    app.run(debug=True, port=5000)






