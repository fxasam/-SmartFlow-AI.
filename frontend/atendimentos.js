(async () => {
    const sessao = window.SmartFlowSessao;
    const lista = document.getElementById("lista-atendimentos");
    const busca = document.getElementById("busca-atendimento");
    const filtroStatus = document.getElementById("filtro-status");
    const filtroCategoria = document.getElementById("filtro-categoria");
    const filtroPrioridade = document.getElementById("filtro-prioridade");
    let atendimentos = [];

    function renderizar() {
        const termo = (busca?.value || "").toLowerCase();
        const itens = atendimentos.filter((a) => {
            return (!termo || JSON.stringify(a).toLowerCase().includes(termo)) &&
                (!filtroStatus?.value || a.status === filtroStatus.value) &&
                (!filtroCategoria?.value || a.categoria === filtroCategoria.value) &&
                (!filtroPrioridade?.value || a.prioridade === filtroPrioridade.value);
        });

        lista.innerHTML = itens.map((a) => `<a class="atendimento-item" href="atendimento.html?id=${a.id}"><div class="atendimento-info"><strong>${a.categoria}</strong><span>${a.resumo_ia || "Sem resumo."}</span></div><div class="atendimento-detalhes"><span>${a.status}</span><span>${a.prioridade}</span></div></a>`).join("") || "<div class='empty-state'>Nenhum atendimento encontrado.</div>";
    }

    await sessao.iniciar();
    atendimentos = await sessao.requisicao("/atendimentos");
    [busca, filtroStatus, filtroCategoria, filtroPrioridade].forEach((el) => el?.addEventListener("input", renderizar));
    renderizar();
})();
