# SmartFlow AI

Central de atendimento inteligente desenvolvida como projeto de portfolio, usando Python, FastAPI, PostgreSQL, Gemini, n8n e frontend em HTML, CSS e JavaScript.

O objetivo do SmartFlow AI e simular uma plataforma de atendimento onde a IA recebe mensagens de clientes, classifica solicitacoes, responde automaticamente quando possivel, consulta pedidos cadastrados e encaminha casos para atendimento humano quando necessario.

## Funcionalidades

- Cadastro e listagem de clientes.
- Cadastro, edicao e listagem de pedidos.
- Consulta automatica de pedidos pelo numero informado pelo cliente.
- Validacao de identidade por CPF ou e-mail antes de retornar dados do pedido.
- Memoria de validacao durante o atendimento, evitando pedir CPF/e-mail novamente no mesmo atendimento.
- Classificacao de mensagens com IA: categoria, prioridade, sentimento, necessidade de atendimento humano e resumo automatico.
- Chat do cliente com link seguro por token.
- Painel administrativo com login.
- Autenticacao com JWT.
- Protecao das rotas administrativas.
- Integracao com n8n para automacoes.
- Envio de respostas humanas pelo painel.
- Dashboard com metricas de atendimentos e pedidos.
- Fila humana para atendimentos que precisam de intervencao.
- Testes automaticos do fluxo de pedidos e validacao.

## Tecnologias utilizadas

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- PyJWT
- bcrypt
- Google Gemini
- n8n
- HTML
- CSS
- JavaScript
- Pytest

## Estrutura do projeto

```text
smartflow-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── atendimentos.py
│   │   │   ├── clientes.py
│   │   │   └── pedidos.py
│   │   ├── auth/
│   │   │   └── security.py
│   │   ├── models/
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   └── ia_service.py
│   │   ├── database.py
│   │   └── main.py
│   └── tests/
│       └── test_atendimentos.py
│
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── atendimentos.html
│   ├── atendimento.html
│   ├── fila.html
│   ├── clientes.html
│   ├── pedidos.html
│   ├── relatorios.html
│   ├── chat.html
│   ├── app.js
│   ├── sessao.js
│   └── style.css
│
├── .env.example
├── .gitignore
└── README.md
```

## Como o sistema funciona

O cliente envia uma mensagem pelo chat. O backend registra o atendimento, salva o historico e usa IA para classificar a solicitacao.

Quando a mensagem envolve entrega, o sistema identifica o numero do pedido e pede CPF ou e-mail para validar se aquele pedido realmente pertence ao cliente. Depois da validacao, o atendimento guarda essa confirmacao durante a conversa, evitando repetir a solicitacao de identificacao.

Quando o atendimento precisa de humano, ele aparece na fila humana. O atendente pode assumir o atendimento, responder pelo painel administrativo e acionar o fluxo do n8n para continuar a automacao.

## Fluxo principal

```text
Cliente
  ↓
Chat publico com token seguro
  ↓
FastAPI
  ↓
PostgreSQL
  ↓
Gemini para classificacao e resposta
  ↓
Dashboard administrativo
  ↓
n8n para automacoes e notificacoes
```

## Seguranca

O projeto possui autenticacao com JWT para o painel administrativo.

As rotas administrativas exigem login valido. O token tem duracao limitada e e armazenado no navegador durante a sessao.

O chat do cliente usa um token proprio por atendimento. Assim, uma pessoa nao consegue abrir uma conversa apenas sabendo o ID do atendimento.

A integracao com n8n usa uma chave propria enviada no cabecalho `X-N8N-Secret`, separada do login do painel administrativo.

## Variaveis de ambiente

O projeto usa um arquivo `.env` na pasta principal.

Exemplo:

```env
GEMINI_API_KEY=sua_chave_do_gemini
JWT_SECRET_KEY=sua_chave_jwt_com_mais_de_32_caracteres
N8N_WEBHOOK_SECRET=sua_chave_secreta_para_o_n8n
DATABASE_URL=postgresql+psycopg2://postgres:sua_senha@localhost:5432/smartflow
```

Importante: o arquivo `.env` nao deve ser enviado para o GitHub.

## Banco de dados

O projeto usa PostgreSQL com o banco `smartflow`.

Algumas tabelas principais:

- `clientes`
- `pedidos`
- `atendimentos`
- `mensagens`
- `usuarios`

Tambem foi adicionada uma chave segura por atendimento:

```text
acesso_cliente_token
```

Essa chave e usada para proteger o acesso do cliente ao chat.

## Principais rotas da API

| Metodo | Rota | Descricao |
|---|---|---|
| POST | `/auth/login` | Realiza login no painel |
| GET | `/auth/me` | Retorna o usuario logado |
| POST | `/auth/registrar` | Cadastra usuario administrador |
| POST | `/atendimentos` | Cria atendimento publico |
| GET | `/atendimentos` | Lista atendimentos no painel |
| GET | `/atendimentos/{id}` | Detalha atendimento no painel ou n8n |
| PATCH | `/atendimentos/{id}/status` | Atualiza status do atendimento |
| POST | `/atendimentos/{id}/mensagens` | Envia mensagem do atendente |
| GET | `/atendimentos/{id}/cliente` | Abre atendimento pelo link seguro do cliente |
| POST | `/atendimentos/{id}/cliente/mensagens` | Envia mensagem pelo chat do cliente |
| GET | `/clientes` | Lista clientes |
| POST | `/pedidos` | Cadastra pedido |
| GET | `/pedidos` | Lista pedidos |
| PATCH | `/pedidos/{id}` | Atualiza pedido |
| GET | `/metricas/resumo` | Retorna metricas do dashboard |

## Como rodar localmente

Entre na pasta do backend:

```bash
cd backend
```

Ative o ambiente virtual:

```bash
..\.venv\Scripts\activate
```

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Inicie o backend:

```bash
uvicorn app.main:app --reload
```

A API ficara disponivel em:

```text
http://127.0.0.1:8000
```

A documentacao Swagger fica em:

```text
http://127.0.0.1:8000/docs
```

Para abrir o frontend, use o Live Server do VS Code na pasta `frontend`.

Exemplo:

```text
http://127.0.0.1:5500/frontend/index.html
```

## Testes

Para rodar os testes automaticos, entre na pasta `backend` e execute:

```bash
..\.venv\Scripts\python.exe -m pytest tests
```

Resultado atual dos testes:

```text
10 passed
```

## Status atual do projeto

O projeto ja possui uma versao funcional localmente com:

- backend conectado ao PostgreSQL;
- IA integrada;
- painel administrativo;
- login com JWT;
- cadastro e edicao de pedidos;
- dashboard com metricas;
- fila humana;
- chat seguro do cliente;
- integracao com n8n;
- testes automaticos passando.

## Proximas melhorias

- Publicar backend, frontend e banco em ambiente online.
- Melhorar responsividade das telas.
- Criar mais testes automaticos para login, pedidos, dashboard e n8n.
- Adicionar imagens do sistema no README.
- Documentar o fluxo do n8n com prints ou export do workflow.

## Autor

Desenvolvido por Samuel da Silva de Souza como projeto de portfolio.
