# Gestão Pecuária

Sistema de gestão de análises de solo e recomendações agronômicas.

API REST em **Django + Django REST Framework** com autenticação **JWT**, e
front-end **Vue 3** (Vue CLI).

## Documentação

| Documento | Conteúdo |
|---|---|
| **[backend/README.md](backend/README.md)** | Instalação e execução da API Django |
| **[frontend/README.md](frontend/README.md)** | Instalação e execução da SPA Vue |

> Existe também um `ERROS_CONHECIDOS.md` com erros de instalação e pendências
> do código, mantido **apenas localmente** (fora do controle de versão).

## Estrutura

```
gestao-pecuaria/
├── backend/                  # API Django — porta 8000
│   ├── config/               # settings, urls, wsgi, asgi
│   ├── apps/
│   │   ├── autenticacao/     # usuário customizado (login por e-mail) + JWT
│   │   └── core/             # produtor, propriedade, laboratório, cultura,
│   │                         # análise de solo, recomendação
│   ├── static/
│   ├── manage.py
│   └── requirements.txt
│
└── frontend/                 # SPA Vue 3 — porta 7777
    ├── src/
    │   ├── views/            # uma tela por rota
    │   ├── router/
    │   ├── store/            # Vuex (registrado, ainda vazio)
    │   └── interceptadorAxios.js
    ├── tests/unit/
    └── package.json
```

## Início rápido

Depende de **Python 3.10–3.12**, **PostgreSQL** e **Node.js 18/20 LTS**.
Os detalhes de cada passo estão nos READMEs de cada parte.

```bash
git clone https://github.com/PatrikiGss/gestao-pecuaria.git
cd gestao-pecuaria
```

**Terminal 1 — backend** (veja [backend/README.md](backend/README.md)):

```bash
cd backend
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

**Terminal 2 — frontend** (veja [frontend/README.md](frontend/README.md)):

```bash
cd frontend
npm install
npm run serve
```

Depois acesse <http://localhost:7777>, crie uma conta em **cadastre-se** e
faça login.

> Antes do `migrate`, é preciso **editar o `.env`** com a senha real do
> PostgreSQL e **criar o banco**. O `.env.example` traz valores de exemplo que
> não funcionam como estão.

## Como as duas partes se conectam

| | Backend | Frontend |
|---|---|---|
| Porta | 8000 | 7777 |
| Endereço | `http://localhost:8000` | `http://localhost:7777` |

A porta 7777 do front é a que está liberada no `CORS_ALLOWED_ORIGINS` e no
`CSRF_TRUSTED_ORIGINS` do backend — mudar uma exige mudar a outra.

A URL da API está **escrita direto no código** do front, não vem de variável de
ambiente. Veja o [README do frontend](frontend/README.md#a-url-da-api-é-fixa-no-código).
