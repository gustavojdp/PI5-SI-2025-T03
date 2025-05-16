async function enviarPergunta() {
    const pergunta = document.getElementById("inputPergunta").value;

    if (!pergunta.trim()) return;

    document.getElementById("resposta").innerText = "Aguarde...";

    const response = await fetch('http://127.0.0.1:5000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pergunta: pergunta }),
    });

    const resposta = await response.json();
    document.getElementById("resposta").innerText = resposta.join("\n");
}
