import spacy

nlp = spacy.load("pt_core_news_sm")

def analisar_texto(texto):
    doc = nlp(texto)

    print("\n🔍 Tokens e lemas:")
    for token in doc:
        print(f"{token.text} → {token.lemma_}")

    print("\n🏷️ Entidades nomeadas:")
    for ent in doc.ents:
        print(f"{ent.text} ({ent.label_})")

    print("\n🧠 Classes gramaticais:")
    for token in doc:
        print(f"{token.text}: {token.pos_}")

if __name__ == "__main__":
    while True:
        texto_exemplo = input("Digite um texto de zoneamento para análise (digite 'sair' para encerrar):\n> ")
        if texto_exemplo.lower() == "sair":
            print("Programa encerrado!")
            break
        analisar_texto(texto_exemplo)
