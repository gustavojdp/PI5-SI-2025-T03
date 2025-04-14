import spacy
from spacy.tokens import DocBin, Span
from mongo_connection import get_mongo_connection  # Não remova esta linha

def criar_descricao_zona(coordenadas, veto):
    descricao = f"Zona com coordenadas: {coordenadas}, com o Veto: {veto}."
    return descricao

def processar_dados():
    db = get_mongo_connection()  # Conectar ao banco de dados MongoDB
    collection = db["SHP"]

    # Consultar dados da coleção SHP
    documentos = collection.find()
    
    # Verificando se documentos foram encontrados
    documento_count = collection.count_documents({})
    if documento_count == 0:
        print("Nenhum documento encontrado na coleção SHP.")
        return
    
    print(f"{documento_count} documentos encontrados na coleção SHP.")
    
    nlp = spacy.blank("pt")
    doc_bin = DocBin()

    for doc in documentos:
        coordenadas = doc["geometry"]["coordinates"][0]  # Pegando as coordenadas do polígono
        veto = doc["properties"]["Veto"]  # Pegando o valor de veto

        # Gerar descrição da zona
        descricao = criar_descricao_zona(coordenadas, veto)
        print(f"Processando zona: {descricao}")  # Mensagem de depuração para verificar a descrição

        # Criar documento spaCy
        spacy_doc = nlp(descricao)

        # Criar as entidades com base na posição
        start = descricao.find("Zona")
        end = start + len("Zona")
        
        # Criar um Span (objeto de entidade)
        span = spacy_doc.char_span(start, end, label="ZONA")

        # Adicionar o Span às entidades do documento
        if span is not None:  # Verifique se o span foi criado corretamente
            spacy_doc.ents = [span]  # Atribui a lista de Spans como entidades do documento
        else:
            print(f"Span não foi criado para a descrição: {descricao}")  # Mensagem de depuração

        # Adicionar ao binário de documentos
        doc_bin.add(spacy_doc)

    # Salvar os dados de treinamento
    doc_bin.to_disk("dados_legislacao.spacy")
    print("Dados de treinamento salvos em 'dados_legislacao.spacy'.")

if __name__ == "__main__":
    processar_dados()
