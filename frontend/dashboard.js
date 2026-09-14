(async () => {
    const sessao = window.SmartFlowSessao;
    const $ = (id) => document.getElementById(id);
    const texto = (id, valor) => { const el = $(id); if (el) el.textContent = valor; };

    function normalizar(status) {
        return String(status || "").toUpperCase();
    }

    function itemAtendimento(atendimento) {
        return `<a class="atendimento-item" href="atendimento.html?id=${atendimento.id}"><div class="atendimento-info"><strong>${atendimento.categoria.toLowerCase()}</strong><span>${atendimento.resumo_ia || "Sem resumo."}</span></div><div class="atendimento-detalhes"><span>${atendimento.status.toLowerCase()}</span><span>${atendimento.prioridade.toLowerCase()}</span></div></a>`;
    }

    async function carregar() {
        await sessao.iniciar();
        const [metricas, atendimentos, pedidos] = await Promise.all([
            sessao.requisicao("/metricas/resumo"),
            sessao.requisicao("/atendimentos"),
            sessao.requisicao("/pedidos"),
        ]);

        texto("atendimentos-hoje", metricas.atendimentos_hoje);
        texto("respondidos-ia", metricas.resolvidos_ia);
        texto("fila-humana", metricas.aguardando_humano);
        texto("urgentes", metricas.urgentes);
        texto("total-pedidos", pedidos.length);
        texto("pedidos-processando", pedidos.filter((p) => normalizar(p.status) === "PROCESSANDO").length);
        texto("pedidos-transporte", pedidos.filter((p) => normalizar(p.status) === "EM_TRANSPORTE").length);
        texto("pedidos-entregues", pedidos.filter((p) => normalizar(p.status) === "ENTREGUE" || normalizar(p.status) === "ENTREGUES").length);

        const lista = $("atendimentos-recentes");
        if (lista) lista.innerHTML = atendimentos.slice(0, 5).map(itemAtendimento).join("") || "<div class='empty-state'>Nenhum atendimento encontrado.</div>";
    }

    $("atualizar-dashboard")?.addEventListener("click", carregar);
    carregar().catch((error) => {
        const msg = $("dashboard-message");
        if (msg) { msg.textContent = error.message; msg.hidden = false; }
    });
})();
