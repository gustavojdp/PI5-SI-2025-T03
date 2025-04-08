# IA de Arquitetura - Verificação de Zoneamento

Uma ferramenta para arquitetos que consulta a legislação de zoneamento com base no CEP ou localização de terrenos.

## Descrição

Este projeto visa facilitar o trabalho de arquitetos ao consultar as regras de zoneamento de terrenos específicos. Utilizando inteligência artificial, o sistema responde a consultas sobre a legislação de uso do solo de acordo com a localização fornecida (CEP ou outra forma de geolocalização).

## Tecnologias Usadas
- **Python 3.10.11**
- **spaCy (python -m spacy download pt_core_news_sm)**
            **(python -m spacy download pt_core_news_md)**
- **geopandas (pip install geopandas)**


## Treinamento
- **python -m spacy init config config.cfg --lang pt --pipeline ner**
- **python -m spacy train config.cfg --output ./output --paths.train ./zona_train.spacy --paths.dev ./zona_train.spacy**
- **python -m spacy train config.cfg --output ./output --gpu-id 0**
