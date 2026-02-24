from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from datetime import datetime, timedelta


URL = "http://normas.receita.fazenda.gov.br/sijut2consulta/consulta.action"


def coletar_atos():
    options = webdriver.ChromeOptions()
    options = webdriver.ChromeOptions()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service("/usr/bin/chromedriver"),
        options=options
    )

    atos = []

    try:
        driver.get(URL)
        wait = WebDriverWait(driver, 20)

        # ===== Intervalo (últimos 3 dias) =====
        data_fim = datetime.today()
        data_inicio = data_fim - timedelta(days=3)

        data_inicio_str = data_inicio.strftime("%d/%m/%Y")
        data_fim_str = data_fim.strftime("%d/%m/%Y")


        # ===== Esperar campo de data =====
        wait.until(EC.presence_of_element_located((By.ID, "dt_inicio")))

        campo_inicio = driver.find_element(By.ID, "dt_inicio")
        campo_inicio.clear()
        campo_inicio.send_keys(data_inicio_str)

        campo_fim = driver.find_element(By.ID, "dt_fim")
        campo_fim.clear()
        campo_fim.send_keys(data_fim_str)

        driver.find_element(By.ID, "btnSubmit").click()

        # ===== Esperar tabela =====
        wait.until(
            EC.presence_of_element_located((By.ID, "tabelaAtos"))
        )

        pagina = 1

        while True:
            print(f"Processando página {pagina}")

            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#tabelaAtos tbody tr.linhaResultados")
                )
            )

            linhas = driver.find_elements(
                By.CSS_SELECTOR,
                "#tabelaAtos tbody tr.linhaResultados"
            )

            if not linhas:
                break

            for linha in linhas:
                colunas = linha.find_elements(By.TAG_NAME, "td")

                if len(colunas) >= 5:
                    atos.append({
                        "tipo_ato": colunas[0].text,
                        "numero": colunas[1].text,
                        "orgao": colunas[2].text,
                        "data_publicacao": colunas[3].text,
                        "ementa": colunas[4].text
                    })

            # ===== Tentar ir para próxima página =====
            try:
                botao_proxima = driver.find_element(By.ID, "btnProximaPagina2")

                if not botao_proxima.is_enabled():
                    break

                primeira_linha = linhas[0]

                botao_proxima.click()

                # Espera a tabela atualizar
                wait.until(EC.staleness_of(primeira_linha))

                pagina += 1

            except NoSuchElementException:
                break

            except TimeoutException:
                break

        print(f"Total capturado: {len(atos)}")

    finally:
        driver.quit()

    return atos