# Gestão Pecuária: projeto-gestao-pecuaria-app.onrender.com

Sistema de gestão de análises de solo e recomendações agronômicas.

O técnico cadastra o laudo do laboratório e o sistema devolve o diagnóstico do
solo e as doses de corretivo e adubo — calculadas por fórmula, a partir dos
parâmetros da cultura, e não estimadas.

Projeto de pesquisa acadêmica. Não substitui o trabalho de um agrônomo nem
emite laudo com responsabilidade técnica.

## Ver funcionando

- Sistema: https://projeto-gestao-pecuaria-app.onrender.com

Basta criar uma conta em "cadastre-se". Cada conta enxerga apenas os próprios
dados.

A hospedagem é gratuita e o servidor da API hiberna após 15 minutos sem uso —
o primeiro acesso do dia pode levar cerca de um minuto para responder. Depois
disso a navegação é normal.

## O que ele calcula

O fluxo do domínio vai do produtor até a recomendação:

```
Produtor → Propriedade → Gleba → Análise de solo → Recomendação
```

A partir dos teores do laudo, o sistema deriva os índices de fertilidade
(soma de bases, CTC efetiva e a pH 7, saturação por bases, saturação por
alumínio, relações Ca:Mg, Ca:K e Mg:K e a classe textural) e, sobre eles,
calcula:

- **Calagem** pelo método da saturação por bases, `NC = T × (V₂ − V₁) / 100`,
  ajustada ao PRNT do calcário cadastrado. Quando a cultura não tem V₂
  definido, cai no método do alumínio e informa qual dos dois usou.
- **Tipo de calcário** pela relação Ca:Mg — dolomítico acima de 4:1,
  magnesiano entre 3 e 4, calcítico abaixo de 3.
- **Gessagem** e as doses de **potássio, fósforo e enxofre**, com as conversões
  saindo da estequiometria.

O cálculo é recusado, com a razão explicada, quando a análise não é da camada
de 0–20 cm: a fórmula da calagem é calibrada para a superfície, e um número
errado calado seria pior que nenhum número.

### O nitrogênio não sai de fórmula

O N disponível depende da mineralização da matéria orgânica, do histórico da
área e da produtividade esperada — nenhum método o deriva de um teor medido no
laudo, e toda tabela de recomendação o trata como função da cultura.

Por isso os parâmetros agronômicos (V₂, saturação de K desejada, fósforo
desejado, fator de fixação, N recomendado, enxofre desejado) são **cadastro**,
preenchidos a partir da fonte que o projeto adotar — Boletim 100 do IAC, 5ª
Aproximação de Minas Gerais, Embrapa Cerrados. O sistema aplica, não arbitra.
Cultura sem parâmetro não trava o cálculo: o que dá para calcular sai, e a
resposta traz a lista do que ficou faltando.

## Tecnologias

Backend em Django 5.0 e Django REST Framework, autenticação JWT e PostgreSQL.
Frontend em Vue 3 com Vue CLI, Bootstrap 5 e axios.

O backend é uma API pura, sem template HTML; o frontend é uma SPA que a
consome. A única cola entre os dois é a variável `VUE_APP_API_URL`.

## Estrutura

```
gestao-pecuaria/
├── backend/                    API Django — porta 8000
│   ├── config/                 settings, urls, wsgi, paginação, exceções
│   └── apps/
│       ├── autenticacao/       usuário com login por e-mail, JWT, perfil
│       ├── core/
│       │   ├── agronomia.py    os cálculos, sem dependência do Django
│       │   ├── models.py       produtor, propriedade, gleba, laboratório,
│       │   │                   cultura, calcário, análise, recomendação
│       │   └── views.py        viewsets isolados por usuário
│       └── validadores.py      CPF, telefone, UF, data, granulometria
│
└── frontend/                   SPA Vue 3 — porta 7777
    └── src/
        ├── views/              uma tela por rota (12 telas)
        ├── estilos/base.css    tokens e classes compartilhadas
        ├── interceptadorAxios.js   JWT com renovação automática
        └── inatividade.js      encerra a sessão após 1h parado
```

O módulo `apps/core/agronomia.py` recebe números e devolve números, sem
importar Django nem conhecer os models. É o que torna cada valor reproduzível
a partir da fórmula e conferível contra a bibliografia.

## Rodando localmente

Requer Python 3.10–3.12 (o Django 5.0 não roda em 3.13+), PostgreSQL 14+ e
Node.js 20 ou superior.

```bash
git clone https://github.com/PatrikiGss/Projeto-gestao-pecuaria.git
cd Projeto-gestao-pecuaria
```

Backend, no primeiro terminal:

```bash
cd backend
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

O `.env` precisa ser preenchido antes do `migrate`: o banco tem que existir e a
senha do PostgreSQL tem que ser a real. Todas as variáveis são obrigatórias —
o Django não sobe se faltar alguma. Os detalhes estão no
[README do backend](backend/README.md).

Frontend, no segundo terminal:

```bash
cd frontend
npm install
npm run serve
```

O sistema fica em http://localhost:7777 e conversa com a API em
http://localhost:8000. A porta 7777 é a liberada em `CORS_ALLOWED_ORIGINS` —
mudar uma exige mudar a outra.

De volta ao backend, para popular o banco com dados de demonstração — incluindo
uma gleba com quatro anos de análises mostrando o solo responder ao manejo:

```bash
python manage.py dados_exemplo --email seu@email.com
```

Tudo o que ele cria fica marcado com `[exemplo]` no nome, e `--limpar` remove
exatamente isso.

## Testes

```bash
cd backend && python -m pytest      # 217 testes
cd frontend && npm run test:unit    # 27 testes
```

A suíte do backend roda contra PostgreSQL e cobre as fórmulas agronômicas com
valores calculados à mão, o isolamento entre contas nos dois sentidos, o
comportamento das exclusões protegidas e a contagem de consultas das listagens
— esta última porque um `select_related` removido por engano não quebra teste
nenhum, só deixa a página lenta em silêncio.

## Licença

[MIT](LICENSE).
