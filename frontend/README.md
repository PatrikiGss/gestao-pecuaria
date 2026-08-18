# Frontend — Gestão Pecuária

SPA em Vue 3 (Vue CLI 5) que consome a API Django deste repositório.

Erros de instalação estão catalogados em `ERROS_CONHECIDOS.md`, na raiz do
projeto (documento local, não versionado).

---

## Pré-requisitos

| Ferramenta | Versão | Observação |
|---|---|---|
| Node.js | **18 ou 20 LTS** | O Vue CLI 5 não recebe mais manutenção; versões novas do Node podem quebrar o build. |

O **backend precisa estar rodando** em `http://localhost:8000` — sem ele, login,
cadastro e todas as telas de CRUD retornam erro de rede. Veja
[backend/README.md](../backend/README.md).

---

## Instalação

Todos os comandos a partir de `gestao-pecuaria/frontend/`.

```bash
npm install
```

```bash
npm run serve
```

A aplicação sobe em <http://localhost:7777>.

A porta é fixada em `vue.config.js` e é a mesma liberada no `CORS_ALLOWED_ORIGINS`
e no `CSRF_TRUSTED_ORIGINS` do backend — trocá-la exige ajustar o
`config/settings.py` do backend também.

---

## Scripts

| Comando | O que faz |
|---|---|
| `npm run serve` | Servidor de desenvolvimento com hot-reload |
| `npm run build` | Build de produção em `dist/` |
| `npm run lint` | ESLint |
| `npm run test:unit` | Testes unitários (mocha + chai) |

---

## Organização

```
src/
├── views/                  # uma tela por rota
│   ├── TelaLogin.vue           /
│   ├── TelaCadastro.vue        /tela-cadastro
│   ├── TelaEdicaoSenha.vue     /tela-edicao
│   ├── TelaUsuario.vue         /tela-usuario
│   ├── TelaProdutor.vue        /tela-produtor
│   ├── TelaPropriedade.vue     /tela-propriedade
│   ├── TelaLaboratorio.vue     /tela-laboratorio
│   ├── TelaCultura.vue         /tela-cultura
│   ├── TelaAnaliseSolo.vue     /tela-analise-solo
│   └── TelaRecomendacoes.vue   /tela-recomendacoes
├── router/index.js         # rotas
├── store/index.js          # Vuex (registrado no main.js, ainda vazio)
├── interceptadorAxios.js   # instância axios + JWT + refresh automático
├── App.vue                 # navbar e controle de sessão
└── main.js
```

Todas as telas são componentes de rota, por isso ficam em `views/`. Não há
componentes reutilizáveis no projeto — se surgirem, criar `src/components/`.

### Sessão e autenticação

`interceptadorAxios.js` exporta uma instância do axios que:

- injeta `Authorization: Bearer <token>` em toda requisição;
- ao receber **401**, tenta renovar o access token com o refresh token e
  reenvia a requisição original;
- enfileira requisições concorrentes enquanto a renovação está em andamento.

Os dados de sessão ficam em `localStorage`: `access_token`, `refresh_token` e
`nome_usuario`. O `App.vue` verifica a presença do `access_token` a cada 3
segundos para mostrar ou esconder a navbar.

---

## A URL da API é fixa no código

Os arquivos `.env`, `.env.development` e `.env.production` definem
`VUE_APP_API_URL`, **mas nenhum arquivo do projeto lê essa variável.** A URL
real está escrita direto no código:

| Arquivo | URL |
|---|---|
| `src/interceptadorAxios.js` | `http://localhost:8000` |
| `src/views/TelaCadastro.vue` | `http://127.0.0.1:8000` (usa `axios` puro, sem passar pelo interceptador) |

Para apontar para outro backend, edite esses dois arquivos.

---

## Testes

```bash
npm run test:unit
```

A cobertura hoje é mínima (`tests/unit/TelaCadastro.spec.js`). Telas que
importam `@/interceptadorAxios` **não são montáveis em teste** por causa de uma
dependência circular (`tela → interceptador → router → tela`), que faz o import
falhar com `Cannot access '__WEBPACK_DEFAULT_EXPORT__' before initialization`.
