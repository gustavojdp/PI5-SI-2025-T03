# 🏙️ Sistema de Consulta de Zoneamento Urbano de Campinas - PI5

Este projeto integra geolocalização, inteligência artificial e análise legislativa para oferecer uma ferramenta de consulta precisa sobre as zonas urbanas de Campinas-SP. Ao inserir um CEP, o sistema retorna a zona correspondente e extrai automaticamente os trechos da **Lei Complementar 208/2018** pertinentes àquele local, com aplicação de NLP (spaCy) para filtragem inteligente dos dispositivos legais.

## ✅ Funcionalidades

- Conversão de CEP em coordenadas geográficas com GoogleV3 do GeoPy
- Localização da zona urbana a partir de dados georreferenciados (MongoDB + Shapely)
- Extração automática de leis específicas da zona (NLP com modelo spaCy treinado)
- Filtragem avançada para garantir sentenças exclusivas da zona consultada

---

## 🚀 Como executar o projeto

### Instale as dependências

```bash
pip install -r requirements.txt
```

### Execute a aplicação principal

```bash
python scripts/consultas/testeSpacy.py
```

---

## ⚙️ Requisitos Mínimos

| Item                | Especificação recomendada         |
|---------------------|-----------------------------------|
| Python              | 3.10.11                           |
| RAM                 | 4 GB ou mais                      |
| MongoDB Atlas       | Acesso a cluster online           |
| Sistema Operacional | Windows 10+ / Linux / macOS       |

---

## 📚 Fontes de Dados

- Lei Complementar nº 208/2018 (Plano Diretor de Campinas)
- Base georreferenciada em formato `.shp` da Prefeitura de Campinas
- Biblioteca spaCy (`pt_core_news_sm`)

---

## 📢 Observações Finais

Este projeto foi desenvolvido como parte do **Projeto Integrador 5 (PI5)** do curso de Sistemas de Informação na PUC-Campinas. O objetivo é demonstrar a aplicação prática de IA e geoprocessamento para uso urbano.
