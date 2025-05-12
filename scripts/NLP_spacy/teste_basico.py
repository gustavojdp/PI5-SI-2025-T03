import spacy

# Carregar o modelo treinado
modelo = spacy.load("modelos/spacy_legislacao_textcat")

# Testar várias frases
frases = [
    "Na ZM1, será permitida a construção de até 5 andares em áreas comerciais.",
    "A tipologia HCSEI em ZC2 tem parâmetros mais restritivos para o número de unidades.",
    "Os lotes de 500m² na ZM2 podem ser parcelados em até 4 unidades habitacionais.",
    "Na ZC4, o uso misto é permitido apenas para edificações de pequeno porte.",
    "Na ZM1-A, a densidade máxima é de 40 unidades habitacionais por hectare."
]

for frase in frases:
    doc = modelo(frase)
    print(f"Frase: {frase}")
    for label, score in doc.cats.items():
        print(f"{label}: {score:.4f}")
    print("-" * 50)
