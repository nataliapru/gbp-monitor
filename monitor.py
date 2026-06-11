import requests
import json
import os

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

LIMITE = 0.4


def cotacao():
    url = "https://economia.awesomeapi.com.br/json/last/GBP-BRL"
    dados = requests.get(url).json()
    return float(dados["GBPBRL"]["bid"])


def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )


def carregar():
    try:
        with open("historico.json") as f:
            return json.load(f)
    except:
        return []


def salvar(h):
    with open("historico.json", "w") as f:
        json.dump(h[-96:], f)


valor = cotacao()

historico = carregar()

if historico:

    anterior = historico[-1]

    variacao = (
        (valor - anterior)
        / anterior
    ) * 100

    media = sum(historico) / len(historico)

    variacao_media = (
        (valor - media)
        / media
    ) * 100


    if abs(variacao) >= LIMITE:

        enviar(
            f"""
🚨 GBP/BRL mudou rápido

Agora: R$ {valor:.2f}

Variação:
{variacao:.2f}%

Última cotação:
R$ {anterior:.2f}
"""
        )


    if variacao_media <= -LIMITE:

        enviar(
            f"""
💷 Possível oportunidade de comprar libra

GBP caiu contra a média recente.

Agora:
R$ {valor:.2f}

Diferença:
{variacao_media:.2f}%
"""
        )


historico.append(valor)

salvar(historico)
