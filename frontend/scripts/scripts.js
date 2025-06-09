async function consultarCEP() {
    const cep = document.getElementById("cepInput").value;
    const output = document.getElementById("resultado");

    if (!cep || cep.length < 8) {
        output.innerText = "⚠️ Por favor, digite um CEP válido de Campinas-SP.";
        return;
    }

    output.innerText = "🔄 Buscando informações...";

    try {
        const response = await fetch(`http://127.0.0.1:5000/buscar?cep=${cep}`);
        const data = await response.json();

        if (!response.ok || data.erro) {
            output.innerText = `❌ Erro: ${data.erro || 'Algo deu errado.'}`;
            return;
        }

        let html = `✅ Zona encontrada: ${data.zona.nome} (${data.zona.codigo})\n`;
        html += `📍 Endereço: ${data.endereco}\n`;
        html += `\n📜 Trechos Legislativos:\n`;

        for (const [topico, frases] of Object.entries(data.legislacao)) {
            html += `\n📌 ${topico.replace(/_/g, ' ')}:\n`;
            frases.slice(0, 5).forEach((frase, i) => {
                html += `  ${i + 1}. ${frase}\n`;
            });
        }

        output.innerText = html;
    } catch (error) {
        output.innerText = `❌ Erro ao consultar o servidor: ${error.message}`;
    }
}

document.getElementById("cepForm").addEventListener("submit", function(e) {
    e.preventDefault(); // Impede o recarregamento
    consultarCEP();
});