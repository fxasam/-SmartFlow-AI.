(async () => {
    const sessao = window.SmartFlowSessao;
    const container = document.getElementById("detalhes-atendimento");
    const id = new URLSearchParams(window.location.search).get("id");

    function mensagemClasse(origem) {
        if (origem === "CLIENTE") return "mensagem-cliente";
        if (origem === "ATENDENTE") return "mensagem-atendente";
        if (origem === "IA") return "mensagem-ia";
        return "mensagem-sistema";
    }

    async function carregar() {
        await sessao.iniciar();
        const atendimento = await sessao.requisicao(`/atendimentos/${id}`);

        container.innerHTML = `<div class="detalhes-grid"><div class="detalhe-card"><span>Categoria</span><strong>${atendimento.categoria}</strong></div><div class="detalhe-card"><span>Prioridade</span><strong>${atendimento.prioridade}</strong></div><div class="detalhe-card"><span>Status</span><strong>${atendimento.status}</strong></div><div class="detalhe-card"><span>Sentimento</span><strong>${atendimento.sentimento}</strong></div></div><div class="detalhe-resumo"><span>Resumo da IA</span><p>${atendimento.resumo_ia || "Sem resumo."}</p></div><div class="cliente-detalhes"><div class="secao-titulo"><span>Cliente</span><h3>${atendimento.cliente.nome}</h3></div><div class="cliente-grid"><div><span>E-mail</span><strong>${atendimento.cliente.email || "-"}</strong></div><div><span>Telefone</span><strong>${atendimento.cliente.telefone || "-"}</strong></div></div></div><div class="historico-atendimento"><div class="secao-titulo"><span>Conversa</span><h3>Historico de mensagens</h3></div><div class="mensagens-lista">${atendimento.mensagens.map((m) => `<div class="mensagem-item ${mensagemClasse(m.origem)}"><div class="mensagem-cabecalho"><strong>${m.origem}</strong><span>${new Date(m.criado_em).toLocaleString("pt-BR")}</span></div><p>${m.conteudo}</p></div>`).join("")}</div></div><form id="resposta-form"><h3>Responder cliente</h3><textarea id="resposta-conteudo" rows="4" placeholder="Digite sua resposta para o cliente..." required></textarea><br><button class="secondary-button" type="submit">Enviar resposta</button></form>`;

        document.getElementById("resposta-form")?.addEventListener("submit", async (event) => {
            event.preventDefault();
            await sessao.requisicao(`/atendimentos/${id}/mensagens`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ origem: "ATENDENTE", conteudo: document.getElementById("resposta-conteudo").value }),
            });
            await carregar();
        });
    }

    carregar().catch((error) => { container.innerHTML = `<div class="empty-state">${error.message}</div>`; });
})();
