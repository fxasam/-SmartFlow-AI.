from datetime import date

from app.api.atendimentos import (
    montar_resposta_pedido,
    parece_identificacao,
    pedido_foi_validado_no_atendimento,
    validar_identidade_cliente,
)
from app.models.models import Cliente, Mensagem, Pedido


def criar_cliente_teste() -> Cliente:
    return Cliente(
        nome="Cliente Teste",
        email="cliente@teste.com",
        cpf="529.982.247-25",
    )


def test_valida_cpf_correto():
    cliente = criar_cliente_teste()

    resultado = validar_identidade_cliente(
        "52998224725",
        cliente,
    )

    assert resultado is True


def test_valida_email_correto():
    cliente = criar_cliente_teste()

    resultado = validar_identidade_cliente(
        "Meu e-mail é cliente@teste.com",
        cliente,
    )

    assert resultado is True


def test_rejeita_cpf_incorreto():
    cliente = criar_cliente_teste()

    resultado = validar_identidade_cliente(
        "111.111.111-11",
        cliente,
    )

    assert resultado is False


def test_rejeita_email_incorreto():
    cliente = criar_cliente_teste()

    resultado = validar_identidade_cliente(
        "outro@teste.com",
        cliente,
    )

    assert resultado is False


def test_identifica_cpf_ou_email():
    assert parece_identificacao(
        "529.982.247-25"
    ) is True

    assert parece_identificacao(
        "cliente@teste.com"
    ) is True


def test_nao_trata_mensagem_comum_como_identificacao():
    resultado = parece_identificacao(
        "Quando meu pedido chega?"
    )

    assert resultado is False


def test_memoria_reconhece_cpf_validado_no_atendimento():
    cliente = criar_cliente_teste()

    historico = [
        Mensagem(
            origem="CLIENTE",
            conteudo="Meu pedido é 548721",
        ),
        Mensagem(
            origem="IA",
            conteudo=(
                "Informe seu CPF ou e-mail "
                "cadastrado na compra."
            ),
        ),
        Mensagem(
            origem="CLIENTE",
            conteudo="529.982.247-25",
        ),
    ]

    resultado = pedido_foi_validado_no_atendimento(
        historico,
        cliente,
    )

    assert resultado is True


def test_memoria_reconhece_email_validado_no_atendimento():
    cliente = criar_cliente_teste()

    historico = [
        Mensagem(
            origem="CLIENTE",
            conteudo="Meu pedido é 548721",
        ),
        Mensagem(
            origem="CLIENTE",
            conteudo="cliente@teste.com",
        ),
    ]

    resultado = pedido_foi_validado_no_atendimento(
        historico,
        cliente,
    )

    assert resultado is True


def test_memoria_nao_valida_dados_incorretos():
    cliente = criar_cliente_teste()

    historico = [
        Mensagem(
            origem="CLIENTE",
            conteudo="Meu pedido é 548721",
        ),
        Mensagem(
            origem="CLIENTE",
            conteudo="111.111.111-11",
        ),
        Mensagem(
            origem="CLIENTE",
            conteudo="outro@teste.com",
        ),
    ]

    resultado = pedido_foi_validado_no_atendimento(
        historico,
        cliente,
    )

    assert resultado is False


def test_monta_resposta_completa_do_pedido():
    pedido = Pedido(
        numero="548721",
        status="EM_TRANSPORTE",
        previsao_entrega=date(2026, 9, 16),
        codigo_rastreio="SF548721BR",
    )

    resposta = montar_resposta_pedido(pedido)

    assert resposta == (
        "Encontrei o pedido 548721. "
        "Ele está com status: em transporte. "
        "A previsão de entrega é 16/09/2026. "
        "Código de rastreio: SF548721BR."
    )
