from transformers import AutoTokenizer, AutoModelForCausalLM

# Carregar o tokenizer e o modelo
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-3B")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-3B")

# Texto de entrada (pergunta sobre zoneamento)
input_text = "Um leão é um mamífero?"



# Tokenizar a entrada
inputs = tokenizer(input_text, return_tensors="pt")

# Gerar a resposta com o modelo
outputs = model.generate(**inputs, max_length=100, num_return_sequences=1, temperature=0.7)

# Decodificar e exibir a resposta gerada
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
