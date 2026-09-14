(() => {
    const API_URL = "http://127.0.0.1:8000";

    function limparSessao() {
        localStorage.removeItem("smartflow_usuario");
        localStorage.removeItem("smartflow_token");
        localStorage.removeItem("smartflow_token_expira_em");
    }

    function sair() {
        limparSessao();
        window.location.replace("index.html");
    }

    function obterToken() {
        const token = localStorage.getItem("smartflow_token");
        if (!token) {
            sair();
            throw new Error("Faca login para acessar o painel.");
        }
        return token;
    }

    async function requisicao(caminho, opcoes = {}) {
        const headers = new Headers(opcoes.headers);
        headers.set("Authorization", `Bearer ${obterToken()}`);

        const response = await fetch(`${API_URL}${caminho}`, {
            ...opcoes,
            headers,
            cache: "no-store",
        });

        if (response.status === 401) {
            sair();
            throw new Error("Sessao expirada. Faca login novamente.");
        }

        if (!response.ok) {
            let mensagem = "Nao foi possivel concluir a operacao.";
            try {
                const dados = await response.json();
                if (typeof dados.detail === "string") mensagem = dados.detail;
            } catch {}
            throw new Error(mensagem);
        }

        if (response.status === 204) return null;
        return response.json();
    }

    async function iniciar() {
        const usuario = await requisicao("/auth/me");
        localStorage.setItem("smartflow_usuario", JSON.stringify(usuario));

        ["usuario-nome", "user-name"].forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.textContent = usuario.nome;
        });

        ["usuario-perfil", "user-profile"].forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.textContent = usuario.perfil;
        });

        document.querySelectorAll(".user-avatar").forEach((el) => {
            el.textContent = usuario.nome?.charAt(0).toUpperCase() || "S";
        });

        return usuario;
    }

    document.addEventListener("click", (event) => {
        if (event.target instanceof Element && event.target.closest("#logout-button")) {
            event.preventDefault();
            sair();
        }
    }, true);

    window.SmartFlowSessao = Object.freeze({ iniciar, requisicao, sair });
})();
