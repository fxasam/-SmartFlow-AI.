# SmartFlow AI 🤖

Central de atendimento inteligente em desenvolvimento, com Python, FastAPI, PostgreSQL, Gemini e n8n.

## Objetivo

Automatizar a triagem de solicitações de clientes, classificando mensagens por categoria, prioridade e sentimento, com geração de respostas e encaminhamento para atendimento humano.

## Arquitetura

- **FastAPI:** API REST, integração com IA e regras de negócio.
- **PostgreSQL e SQLAlchemy:** armazenamento de clientes, atendimentos e mensagens.
- **Gemini:** classificação e geração de respostas.
- **n8n:** orquestração de webhooks e fluxos de atendimento.
- **HTML, CSS e JavaScript:** interface web.

## Progresso do desenvolvimento

Durante o desenvolvimento local, foram realizados testes de:

- Registro e classificação de solicitações pela API.
- Integração entre backend, PostgreSQL e Gemini.
- Encaminhamento para fila humana.
- Respostas e notificações por fluxos do n8n.
- Histórico de mensagens e dados do cliente.

A interface de login e dashboard também está em desenvolvimento.

## Regras de encaminhamento

O projeto prevê atendimento humano obrigatório quando:

- A confiança informada pela IA é inferior a 80%.
- A prioridade é urgente.
- A solicitação envolve financeiro ou cancelamento.

A confiança retornada pela IA é utilizada como sinal de triagem, sem representar garantia de acerto.

## Endpoints definidos

| Método | Rota | Finalidade |
| --- | --- | --- |
| POST | /atendimentos | Registrar e classificar |
| GET | /atendimentos | Listar e filtrar |
| GET | /atendimentos/{id} | Consultar detalhes |
| PATCH | /atendimentos/{id}/status | Atualizar status |
| POST | /atendimentos/{id}/mensagens | Adicionar mensagem |
| GET | /metricas/resumo | Consultar indicadores |

## Estado deste repositório

Esta publicação inicial apresenta a documentação do projeto e o progresso registrado durante seu desenvolvimento.

O código-fonte original e as instruções de execução serão adicionados após a revisão dos arquivos locais. Este repositório ainda não contém uma versão executável.

## Próximos passos

- Importar e revisar o código-fonte original.
- Documentar instalação e configuração.
- Concluir e validar a integração da interface.
- Adicionar testes reproduzíveis e exemplos de uso.

## Autor

**Samuel da Silva de Souza**
Estudante de Análise e Desenvolvimento de Sistemas.

[GitHub](https://github.com/fxasam) · [Projeto DOCIA](https://github.com/fxasam/DOCIA)
