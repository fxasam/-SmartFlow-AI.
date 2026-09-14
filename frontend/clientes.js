(async () => {
    const sessao = window.SmartFlowSessao;
    const lista = document.getElementById("clientes-lista");

    await sessao.iniciar();
    const clientes = await sessao.requisicao("/clientes");

    lista.innerHTML = clientes.map((c) => `<article class="atendimento-item"><div class="atendimento-info"><strong>${c.nome}</strong><span>${c.email || "Sem e-mail"}</span><span>${c.telefone || "Sem telefone"}</span></div><div class="atendimento-detalhes"><span>${c.total_atendimentos} atendimentos</span></div></article>`).join("") || "<div class='empty-state'>Nenhum cliente encontrado.</div>";
})();
