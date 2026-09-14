(async () => {
    const sessao = window.SmartFlowSessao;
    const form = document.getElementById("pedido-form");
    const lista = document.getElementById("pedidos-lista");
    const clienteSelect = document.getElementById("cliente-id");
    let pedidoEditando = null;

    function valor(id) { return document.getElementById(id).value; }

    async function carregar() {
        const [clientes, pedidos] = await Promise.all([
            sessao.requisicao("/clientes"),
            sessao.requisicao("/pedidos"),
        ]);

        clienteSelect.innerHTML = '<option value="">Selecione um cliente</option>' + clientes.map((c) => `<option value="${c.id}">${c.nome}</option>`).join("");
        lista.innerHTML = pedidos.map((p) => `<article class="atendimento-item"><div class="atendimento-info"><strong>Pedido ${p.numero}</strong><span>Previsao: ${p.previsao_entrega || "-"}</span><span>Rastreio: ${p.codigo_rastreio || "-"}</span></div><div class="atendimento-detalhes"><span>${p.status.toLowerCase()}</span><button class="secondary-button" data-editar="${p.id}">Editar</button></div></article>`).join("") || "<div class='empty-state'>Nenhum pedido encontrado.</div>";
    }

    await sessao.iniciar();
    await carregar();

    form?.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
            cliente_id: valor("cliente-id"),
            numero: valor("pedido-numero"),
            status: valor("pedido-status"),
            previsao_entrega: valor("pedido-previsao") || null,
            codigo_rastreio: valor("pedido-rastreio") || null,
        };

        await sessao.requisicao(pedidoEditando ? `/pedidos/${pedidoEditando}` : "/pedidos", {
            method: pedidoEditando ? "PATCH" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        pedidoEditando = null;
        form.reset();
        await carregar();
    });
})();
