document.getElementById("cepForm").addEventListener("submit", async function(e) {
  e.preventDefault();
  const cep = document.getElementById("cepInput").value;
  const resultado = document.getElementById("resultado");
  resultado.innerHTML = "<p class='thinking'>🔄 Buscando informações...</p>";

  try {
    const response = await fetch(`http://127.0.0.1:5000/buscar?cep=${cep}`);
    const data = await response.json();

    if (data.zona) {
      let html = `<div class='response'><h2>Zona encontrada: ${data.zona.nome} (${data.zona.codigo})</h2>`;
      html += `<p><strong>Endereço:</strong> ${data.endereco}</p>`;
      html += `<h3>📄 Trechos Legislativos:</h3>`;

      for (const [topico, frases] of Object.entries(data.legislacao)) {
        html += `<div class='topico'><h4>${topico.replace(/_/g, ' ')}</h4><ul>`;
        frases.forEach(frase => {
          html += `<li>${frase}</li>`;
        });
        html += `</ul></div>`;
      }

      html += `</div>`;
      resultado.innerHTML = html;
    } else {
      resultado.innerHTML = `<p class='erro'>❌ Nenhuma zona encontrada para o CEP informado.</p>`;
    }
  } catch (error) {
    resultado.innerHTML = `<p class='erro'>⚠️ Erro ao buscar dados: ${error.message}</p>`;
  }
});