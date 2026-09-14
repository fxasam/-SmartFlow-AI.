import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError


load_dotenv("../.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


def chamar_gemini(prompt: str):
    tentativas = 3

    for tentativa in range(tentativas):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
            )
            return response
        except ServerError as erro:
            if tentativa == tentativas - 1:
                raise erro

            print(f"Gemini indisponivel. Tentativa {tentativa + 1}/{tentativas}. Tentando novamente...")
            time.sleep(2)


def classificar_mensagem(mensagem: str):
    prompt = f"""
Voce e um classificador de atendimento ao cliente.

Analise a mensagem abaixo e responda SOMENTE com JSON valido.

Formato obrigatorio:

{{
    "categoria": "ENTREGA|FINANCEIRO|CANCELAMENTO|SUPORTE|INFORMACAO|RECLAMACAO|OUTROS",
    "prioridade": "BAIXA|MEDIA|ALTA|URGENTE",
    "sentimento": "POSITIVO|NEUTRO|NEGATIVO",
    "precisa_humano": true,
    "confianca": 0.0,
    "resumo": "resumo curto"
}}

Mensagem do cliente:
{mensagem}
"""

    response = chamar_gemini(prompt)
    texto = response.text.strip()

    if texto.startswith("```json"):
        texto = texto.replace("```json", "").replace("```", "").strip()

    resultado = json.loads(texto)
    categoria = resultado.get("categoria", "OUTROS")
    prioridade = resultado.get("prioridade", "MEDIA")
    confianca = float(resultado.get("confianca", 0))

    resultado["precisa_humano"] = confianca < 0.80 or prioridade == "URGENTE" or categoria in ["FINANCEIRO", "CANCELAMENTO"]

    return resultado


def gerar_resposta_automatica(mensagem: str, classificacao: dict):
    prompt = f"""
Voce e o atendente virtual do SmartFlow AI.

Responda ao cliente em portugues do Brasil.

Regras:

- Seja educado.
- Seja breve.
- Seja objetivo.
- Nao invente informacoes.
- Nao invente prazo de entrega.
- Nao invente numero de pedido.
- Nao invente politicas da empresa.
- Nao solicite senha.
- Nao solicite dados bancarios.
- Nao prometa algo que nao foi confirmado.
- Use apenas as informacoes disponiveis.

Classificacao do atendimento:

Categoria:
{classificacao["categoria"]}

Prioridade:
{classificacao["prioridade"]}

Sentimento:
{classificacao["sentimento"]}

Resumo:
{classificacao["resumo"]}

Mensagem do cliente:
{mensagem}

Responda somente com a mensagem que sera enviada ao cliente.
"""

    response = chamar_gemini(prompt)
    return response.text.strip()


def gerar_resposta_com_historico(historico: list):
    conversa = []

    for mensagem in historico:
        origem = mensagem.origem
        conteudo = mensagem.conteudo

        if origem == "CLIENTE":
            papel = "Cliente"
        elif origem == "IA":
            papel = "Atendente virtual"
        elif origem == "ATENDENTE":
            papel = "Atendente humano"
        else:
            papel = "Sistema"

        conversa.append(f"{papel}: {conteudo}")

    historico_formatado = "\n".join(conversa)

    prompt = f"""
Voce e o atendente virtual do SmartFlow AI.

Continue o atendimento abaixo levando em consideracao todo o historico da conversa.

Regras:

- Responda em portugues do Brasil.
- Seja educado.
- Seja breve.
- Seja objetivo.
- Considere as mensagens anteriores.
- Nao repita perguntas que o cliente ja respondeu.
- Nao invente informacoes.
- Nao invente prazo de entrega.
- Nao invente numero de pedido.
- Nao invente politicas da empresa.
- Nao solicite senha.
- Nao solicite dados bancarios.
- Nao prometa algo que nao foi confirmado.
- Se precisar de uma informacao que ainda nao foi fornecida, pergunte ao cliente.
- Use apenas as informacoes presentes na conversa.

Historico do atendimento:

{historico_formatado}

Responda somente com a proxima mensagem que deve ser enviada ao cliente.
"""

    response = chamar_gemini(prompt)
    return response.text.strip()
