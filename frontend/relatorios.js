(async () => {
    const sessao = window.SmartFlowSessao;
    const texto = (id, valor) => { const el = document.getElementById(id); if (el) el.textContent = valor; };

    await sessao.iniciar();
    const atendimentos = await sessao.requisicao("/atendimentos");

    texto("total-atendimentos", atendimentos.length);
    texto("respondidos-ia", atendimentos.filter((a) => a.status === "RESPONDIDO_IA").length);
    texto("atendimentos-humanos", atendimentos.filter((a) => a.precisa_humano).length);
    texto("total-resolvidos", atendimentos.filter((a) => a.status === "RESOLVIDO").length);
})();
