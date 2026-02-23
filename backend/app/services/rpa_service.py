import time
from datetime import datetime

import requests

from app.core.settings import settings
from app.rpa.scraper_selenium import coletar_atos

API_BASE_URL = settings.api_base_url.rstrip("/")
API_URL = f"{API_BASE_URL}/atos/batch"
LOGIN_URL = f"{API_BASE_URL}/auth/login"


def obter_token() -> str:
    response = requests.post(
        LOGIN_URL,
        data={
            "username": settings.admin_username,
            "password": settings.admin_password,
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise Exception("Falha na autenticação com a API")

    return response.json()["access_token"]


def executar_rpa():
    inicio = time.time()

    token = obter_token()
    headers = {"Authorization": f"Bearer {token}"}

    atos_coletados = coletar_atos()

    dados_formatados = [
        {
            "tipo_ato": ato["tipo_ato"],
            "numero_ato": ato["numero"],
            "orgao_unidade": ato["orgao"],
            "publicacao": datetime.strptime(
                ato["data_publicacao"], "%d/%m/%Y"
            ).date().isoformat(),
            "ementa": ato["ementa"],
        }
        for ato in atos_coletados
    ]

    response = requests.post(
        API_URL,
        json=dados_formatados,
        headers=headers,
        timeout=60,
    )

    tempo_execucao = time.time() - inicio

    if response.status_code != 200:
        return {
            "status_code_api": response.status_code,
            "erro_api": response.text,
            "tempo_execucao_rpa": tempo_execucao,
        }

    return {
        "status_code_api": response.status_code,
        "resposta_api": response.json(),
        "tempo_execucao_rpa": tempo_execucao,
    }
