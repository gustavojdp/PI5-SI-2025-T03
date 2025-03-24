import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Carregar o tokenizer e o modelo
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B")

# Configurar dispositivo
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

def gerar_resposta(prompt, max_length=150, temperature=0.7):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_length=max_length, temperature=temperature, num_return_sequences=1)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Loop de interação com o usuário
print("==== Modo Interativo ====")
print("Digite 'sair' para encerrar.\n")

while True:
    prompt = input("Digite sua pergunta: ")
    if prompt.lower() == "sair":
        break

    try:
        temp = float(input("Temperatura (ex: 0.3, 0.7, 1.0): "))
    except ValueError:
        print("Temperatura inválida! Usando valor padrão 0.7.")
        temp = 0.7

    resposta = gerar_resposta(prompt, temperature=temp)
    print(f"\n🧠 Resposta:\n{resposta}\n{'-'*60}")
