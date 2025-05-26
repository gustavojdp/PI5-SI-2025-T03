from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import re

# Configura o navegador (modo headless opcional)
options = Options()
options.add_argument("--start-maximized")
# options.add_argument("--headless")  # descomente para rodar sem abrir janela

# Caminho do seu ChromeDriver deve estar configurado no PATH
driver = webdriver.Chrome(options=options)

try:
    # Abre o site
    driver.get("https://zoneamento.campinas.sp.gov.br/#")
    time.sleep(5)

    # Exibe mensagem para o usuário interagir com o pop-up manualmente
    input("🕐 Por favor, clique manualmente em 'Concordar' no pop-up do site e pressione ENTER para continuar...")

    # Aguarda o carregamento do mapa
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "leaflet-container"))
    )
    time.sleep(3)

    # Centraliza o mapa em Campinas (ex: Barão Geraldo) com zoom adequado
    driver.execute_script("map.setView([-22.8284, -47.1046], 14);")
    time.sleep(2)

    # Clica em um ponto visível e interativo do mapa
    mapa = driver.find_element(By.CLASS_NAME, "leaflet-container")
    ActionChains(driver).move_to_element_with_offset(mapa, 400, 300).click().perform()
    time.sleep(3)

    # Solicita ao usuário clicar em "Mais Informações"
    input("🔍 Clique em 'Mais Informações' no popup e pressione ENTER para continuar com a extração...")

    # Aguarda o modal de detalhes aparecer
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "detalhes_zoneamento"))
    )
    modal = driver.find_element(By.CSS_SELECTOR, "#detalhes_zoneamento .modal-content.animate")
    html_modal = modal.get_attribute("innerHTML")
    soup = BeautifulSoup(html_modal, "html.parser")
    texto = soup.get_text("\n").strip()

    # Regex para código cartográfico
    match_cod = re.search(r"\b\d{4}\.\d{2}\.\d{2}\.\d{4}\b", texto)

    # Para zona, procurar por linha que contenha só a zona após "Zoneamento"
    zona = "Não encontrado"
    linhas = texto.split("\n")
    for i, linha in enumerate(linhas):
        if "Zoneamento" in linha and i + 1 < len(linhas):
            proxima = linhas[i + 1].strip()
            if re.match(r"Z[ACDEHLMRSU][A-Z0-9-]*", proxima):
                zona = proxima
                break

    dados = {
        "codigo_cartografico": match_cod.group(0) if match_cod else "Não encontrado",
        "zona": zona,
        "ocupacoes": [a.text for a in soup.find_all("a") if any(k in a.text for k in ["CSEI", "HMH", "HU", "HCSEI"])],
        "links": [a['href'] for a in soup.find_all("a") if a.get("href")],
        "texto_bruto": texto
    }

    # Salva em JSON
    with open("output/dados_extraidos_popup.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

    print("✅ Extração concluída com sucesso!")

except Exception as e:
    print("❌ Erro na execução:", str(e))

finally:
    driver.quit()
