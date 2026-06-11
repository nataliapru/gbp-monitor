import requests
import json
import os
from datetime import date

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

IOF = 0.011
SPREAD_WISE = 0.007


def cotacao():
    url = "https://open.er-api.com/v6/latest/GBP"
    dados = requests.get(url).json()

    if dados["result"] != "success":
        raise Exception(dados)

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


def compra_diaria():

    hoje = date.today()

    if hoje <= date(2026, 6, 24):
        return 103

    if hoje <= date(2026, 7, 3):
        return 89.60

    return 0


valor = cotacao()

valor_wise = valor * (1 + SPREAD_WISE) * (1 + IOF)

historico = carregar()


if historico:

    media = sum(historico) / len(historico)

    queda = ((valor - media) / media) * 100

    dias = 0

    if queda <= -1.2:
        dias = 5

    elif queda <= -0.8:
        dias = 3

    elif queda <= -0.4:
        dias = 1


    if dias:

        libras = compra_diaria() * dias

        economia = (
            (media - valor)
            * libras
        )

        enviar(
f"""💷 Oportunidade GBP/BRL

Cotação Wise estimada:
R$ {valor_wise:.2f}/£

Variação contra média:
{queda:.2f}%

Sugestão:
comprar £{libras:.2f}

Equivale a antecipar:
{dias} dia(s)

Economia aproximada:
R$ {economia:.2f}
"""
        )


historico.append(valor)

salvar(historico)
