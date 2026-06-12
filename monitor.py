import requests
import json
import os
from datetime import date, datetime, timedelta

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
AWESOME_API_KEY = os.environ["AWESOME_API_KEY"]

IOF = 0.011
SPREAD_WISE = 0.007


def cotacao():
    url = (
        "https://economia.awesomeapi.com.br/json/last/GBP-BRL"
        f"?token={AWESOME_API_KEY}"
    )

    dados = requests.get(url).json()

    if "GBPBRL" not in dados:
        raise Exception(dados)

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


def carregar_json(nome, padrao):
    try:
        with open(nome) as f:
            return json.load(f)
    except:
        return padrao


def salvar_json(nome, dados):
    with open(nome, "w") as f:
        json.dump(dados, f)


def compra_diaria():

    hoje = date.today()

    if hoje <= date(2026, 6, 24):
        return 103

    if hoje <= date(2026, 7, 3):
        return 89.60

    return 0


# =====================
# COTAÇÃO ATUAL
# =====================

valor = cotacao()

valor_wise = valor * (1 + SPREAD_WISE) * (1 + IOF)


# =====================
# HISTÓRICO 24H
# =====================

historico = carregar_json("historico.json", [])

# compatibilidade com histórico antigo
if historico and isinstance(historico[0], float):
    historico = [
        {
            "data": datetime.now().isoformat(),
            "valor": x
        }
        for x in historico
    ]


if historico:

    valores = [x["valor"] for x in historico]

    maxima_24h = max(valores)

    media_24h = sum(valores) / len(valores)

    queda_maxima = ((valor - maxima_24h) / maxima_24h) * 100

    queda_media = ((valor - media_24h) / media_24h) * 100


    nivel = 0
    dias = 0

    if queda_maxima <= -1.2:
        nivel = 3
        dias = 5

    elif queda_maxima <= -0.8:
        nivel = 2
        dias = 3

    elif queda_maxima <= -0.4:
        nivel = 1
        dias = 1


    alerta = carregar_json(
        "alerta.json",
        {"nivel": 0}
    )


    # saiu da zona de oportunidade
    if nivel == 0:
        alerta["nivel"] = 0
        salvar_json("alerta.json", alerta)


    # nova oportunidade ou queda aumentou
    elif nivel > alerta.get("nivel", 0):

        libras = compra_diaria() * dias

        economia = (
            (maxima_24h - valor)
            * libras
        )

        enviar(
f"""💷 Oportunidade GBP/BRL

Cotação Wise estimada:
R$ {valor_wise:.4f}/£

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

        alerta["nivel"] = nivel
        salvar_json(
            "alerta.json",
            alerta
        )


# =====================
# SALVAR HISTÓRICO
# =====================

historico.append(
    {
        "data": datetime.now().isoformat(),
        "valor": valor
    }
)

limite = datetime.now() - timedelta(hours=24)

historico = [
    item for item in historico
    if datetime.fromisoformat(item["data"]) >= limite
]

salvar_json(
    "historico.json",
    historico
)
