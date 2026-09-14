(() => {
    const API_URL = "http://127.0.0.1:8000";
    const form = document.querySelector("form");

    if (!form) return;

    const emailInput = form.querySelector('input[type="email"]');
    const senhaInput = form.querySelector('input[type="password"]');
    const botao = form.querySelector('button[type="submit"], button:not([type])');
    const mensagem = document.createElement("p");

    mensagem.setAttribute("role", "alert");
    mensagem.style.color = "#b91c1c";
    mensagem.style.marginBottom = "16px";
    mensagem.hidden = true;
    form.prepend(mensagem);

    function limparSessao() {
        localStorage.removeItem("smartflow_usuario");
        localStorage.removeItem("smartflow_token");
        localStorage.removeItem("smartflow_token_expira_em");
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        mensagem.hidden = true;
        botao.disabled = true;
        botao.textContent = "Entrando...";
        limparSessao();

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: emailInput.value.trim(), senha: senhaInput.value }),
            });

            const dados = await response.json();

            if (!response.ok) throw new Error(dados.detail || "Nao foi possivel fazer login.");

            localStorage.setItem("smartflow_token", dados.access_token);
            localStorage.setItem("smartflow_token_expira_em", String(Date.now() + dados.expires_in * 1000));
            localStorage.setItem("smartflow_usuario", JSON.stringify(dados.usuario));
            window.location.replace("dashboard.html");
        } catch (error) {
            limparSessao();
            mensagem.textContent = error.message || "Nao foi possivel fazer login.";
            mensagem.hidden = false;
        } finally {
            botao.disabled = false;
            botao.textContent = "Entrar";
        }
    });
})();
