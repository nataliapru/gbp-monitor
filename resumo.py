import requests
import os
from datetime import date

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

IOF = 0.011
SPREAD_WISE = 0.007


def cotacao():
    url = "https://open.er-api.com/v6/latest/GBP"
    dados = requests.get(url).json()
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


hoje = date.today()

if hoje <= date(2026, 6, 24):
    libras = 103

elif hoje <= date(2026, 7, 3):
    libras = 89.60

else:
    libras = 0


valor = cotacao()

wise = valor * (1 + IOF) * (1 + SPREAD_WISE)

custo = wise * libras


enviar(
f"""📊 GBP/BRL — Plano diário

Cotação Wise estimada:
R$ {wise:.2f}/£

Compra planejada hoje:
£{libras:.2f}

Custo aproximado:
R$ {custo:.2f}

Continuo monitorando oportunidades."""
)
