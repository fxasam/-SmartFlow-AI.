const API_URL = "http://127.0.0.1:8000";
const chatMensagens = document.getElementById("chat-mensagens");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatEnviar = document.getElementById("chat-enviar");
const parametros = new URLSearchParams(window.location.search);
const atendimentoId = parametros.get("id");
const tokenCliente = parametros.get("token");

function escaparHTML(valor) {
    return String(valor ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
}

function formatarMensagem(mensagem) {
    let classe = "chat-mensagem-ia";
    let nome = "SmartFlow AI";
    if (mensagem.origem === "CLIENTE") { classe = "chat-mensagem-cliente"; nome = "Voce"; }
    if (mensagem.origem === "ATENDENTE") nome = "Atendente";
    return `<div class="chat-mensagem ${classe}"><div class="chat-balao"><strong>${nome}</strong><p>${escaparHTML(mensagem.conteudo).replaceAll("\n", "<br>")}</p></div></div>`;
}

function bloquearChat() {
    chatInput.disabled = true;
    chatEnviar.disabled = true;
}

function urlConversa() {
    return `${API_URL}/atendimentos/${atendimentoId}/cliente?token=${encodeURIComponent(tokenCliente)}`;
}

function urlEnviar() {
    return `${API_URL}/atendimentos/${atendimentoId}/cliente/mensagens?token=${encodeURIComponent(tokenCliente)}`;
}

async function carregarConversa() {
    if (!atendimentoId || !tokenCliente) {
        chatMensagens.innerHTML = `<div class="empty-state"><strong>Link de conversa invalido</strong><p>Use o link completo enviado pelo SmartFlow.</p></div>`;
        bloquearChat();
        return;
    }

    const response = await fetch(urlConversa());
    if (!response.ok) {
        bloquearChat();
        chatMensagens.innerHTML = `<div class="empty-state"><strong>Link de conversa invalido</strong><p>Use o link completo enviado pelo SmartFlow.</p></div>`;
        return;
    }

    const atendimento = await response.json();
    chatMensagens.innerHTML = atendimento.mensagens.map(formatarMensagem).join("");
    chatMensagens.scrollTop = chatMensagens.scrollHeight;
}

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const conteudo = chatInput.value.trim();
    if (!conteudo) return;

    chatInput.disabled = true;
    chatEnviar.disabled = true;
    chatEnviar.textContent = "Enviando...";

    try {
        await fetch(urlEnviar(), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ conteudo }),
        });
        chatInput.value = "";
        await carregarConversa();
    } finally {
        chatInput.disabled = false;
        chatEnviar.disabled = false;
        chatEnviar.textContent = "Enviar";
        chatInput.focus();
    }
});

carregarConversa();
