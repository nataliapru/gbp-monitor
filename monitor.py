import requests
import json
import os
from datetime import date, datetime, timedelta

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
            dados = json.load(f)

            # converte histórico antigo, se existir
            if dados and isinstance(dados[0], float):
                return [
                    {
                        "data": datetime.now().isoformat(),
                        "valor": x
                    }
                    for x in dados
                ]

            return dados

    except:
        return []


def salvar(h):
    limite = datetime.now() - timedelta(hours=24)

    h = [
        item for item in h
        if datetime.fromisoformat(item["data"]) >= limite
    ]

    with open("historico.json", "w") as f:
        json.dump(h, f)


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

    valores = [x["valor"] for x in historico]

    maxima_24h = max(valores)

    media_24h = sum(valores) / len(valores)

    queda_maxima = ((valor - maxima_24h) / maxima_24h) * 100

    queda_media = ((valor - media_24h) / media_24h) * 100


    dias = 0

    if queda_maxima <= -1.2:
        dias = 5

    elif queda_maxima <= -0.8:
        dias = 3

    elif queda_maxima <= -0.4:
        dias = 1


    if dias:

        libras = compra_diaria() * dias

        economia = (
            (maxima_24h - valor)
            * libras
        )

        enviar(
f"""💷 Oportunidade GBP/BRL

Cotação Wise estimada:
R$ {valor_wise:.2f}/£

Queda desde máxima 24h:
{queda_maxima:.2f}%

Comparação com média 24h:
{queda_media:.2f}%

Sugestão:
comprar £{libras:.2f}

Antecipação:
{dias} dia(s)

Economia aproximada:
R$ {economia:.2f}
"""
        )


historico.append(
    {
        "data": datetime.now().isoformat(),
        "valor": valor
    }
)

salvar(historico)
