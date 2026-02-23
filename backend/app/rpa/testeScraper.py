from scraper_selenium import coletar_atos

atos = coletar_atos()

if atos:
    print("Primeiro registro:", atos[0])
else:
    print("Nenhum encontrado")