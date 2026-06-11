import requests
import json
import os

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

LIMITE = 0.4


def cotacao():
    url = "https://open.er-api.com/v6/latest/GBP"

    resposta = requests.get(url)
    dados = resposta.json()

    if dados["result"] != "success":
        raise Exception(f"Erro ao buscar cotação: {dados}")

    return float(dados["rates"]["BRL"])


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

    variacao = ((valor - anterior) / anterior) * 100

    media = sum(historico) / len(historico)

    variacao_media = ((valor - media) / media) * 100


    if abs(variacao) >= LIMITE:

        enviar(
            f"""🚨 GBP/BRL mudou rápido

Cotação atual:
R$ {valor:.2f}

Variação desde a última leitura:
{variacao:.2f}%

Anterior:
R$ {anterior:.2f}
"""
        )


    if variacao_media <= -LIMITE:

        enviar(
            f"""💷 Possível oportunidade de comprar libra

A libra caiu em relação à média recente.

Agora:
R$ {valor:.2f}

Diferença:
{variacao_media:.2f}%
"""
        )


else:
    enviar(
        f"""✅ Monitor GBP/BRL iniciado

Primeira cotação registrada:
R$ {valor:.2f}

Agora vou acompanhar a cada 15 minutos."""
    )


historico.append(valor)

salvar(historico)

enviar("🧪 Teste: o robô GBP Monitor está conectado ao Telegram.")
