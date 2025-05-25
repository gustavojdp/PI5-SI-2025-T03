import spacy
from spacy.language import Language
from spacy.tokens import Doc
import json

# --- Registro do custom_summarizer ------------------------------------------------

class CustomSummarizer:
    def __init__(self, nlp, name, max_length=500, preserve_entities=True):
        self.max_length = int(max_length)
        self.preserve_entities = preserve_entities

    def __call__(self, doc: Doc) -> Doc:
        resumo = ""
        for sent in doc.sents:
            if len(resumo) + len(sent.text) <= self.max_length:
                resumo += sent.text.strip() + " "
            else:
                break
        doc._.summary = resumo.strip()
        return doc

# cria o atributo ._.summary em todo Doc
Doc.set_extension("summary", default="")

# registra a fábrica para o nome “custom_summarizer”
@Language.factory(
    "custom_summarizer",
    default_config={"max_length": 500, "preserve_entities": True}
)
def create_summarizer(nlp, name, max_length, preserve_entities):
    return CustomSummarizer(nlp, name, max_length, preserve_entities)

# ----------------------------------------------------------------------------------

# Carregar o modelo treinado
modelo = spacy.load("modelos/spacy_legislacao_textcat")

# Adiciona o sentencizer no início da pipeline se não existir
if "sentencizer" not in modelo.pipe_names:
    modelo.add_pipe("sentencizer", first=True)

# Adiciona o custom_summarizer no fim da pipeline se não existir
if "custom_summarizer" not in modelo.pipe_names:
    modelo.add_pipe("custom_summarizer", last=True)

# Carregar legislações
with open("zonas_legislacao_extraida_atualizado.json", "r", encoding="utf-8") as f:
    legislacoes = json.load(f)

def obter_resposta(pergunta):
    doc = modelo(pergunta)
    categoria = max(doc.cats, key=doc.cats.get)
    print(f"Categoria identificada: {categoria}")

    resposta = []
    for zona, trechos in legislacoes.items():
        if categoria in zona.lower():
            for trecho in trechos:
                if categoria in trecho.lower():
                    tdoc = modelo(trecho)
                    resumo = tdoc._.summary

                    linhas_limpas = [
                        linha.strip()
                        for linha in resumo.splitlines()
                        if linha.strip() and linha.strip("-") != ""
                    ]
                    resumo_limpo = " ".join(linhas_limpas)
                    if resumo_limpo:
                        resposta.append(resumo_limpo)

    return resposta



if __name__ == "__main__":
    while True:
        pergunta = input("\nDigite sua pergunta (ou 'sair' para encerrar): ")
        if pergunta.lower() == "sair":
            print("Saindo...")
            break

        resposta = obter_resposta(pergunta)
        if resposta:
            print("\nResposta encontrada:")
            for trecho in resposta:
                print(f"- {trecho}")
        else:
            print("\nDesculpe, não encontrei uma resposta relevante.")
