(async () => {
    const sessao = window.SmartFlowSessao;
    const lista = document.getElementById("fila-lista");

    await sessao.iniciar();
    const atendimentos = await sessao.requisicao("/atendimentos?status=FILA_HUMANA");

    lista.innerHTML = atendimentos.map((a) => `<a class="atendimento-item" href="atendimento.html?id=${a.id}"><div class="atendimento-info"><strong>${a.categoria}</strong><span>${a.resumo_ia || "Atendimento aguardando humano."}</span></div><div class="atendimento-detalhes"><span>${a.prioridade}</span><span>${a.status}</span></div></a>`).join("") || "<div class='empty-state'>Fila vazia.</div>";
})();
