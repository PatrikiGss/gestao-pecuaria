# Backend — Gestão Pecuária

API REST em Django 5.0 + Django REST Framework, autenticação JWT
(`djangorestframework-simplejwt`) e PostgreSQL.

Erros de instalação estão catalogados em `ERROS_CONHECIDOS.md`, na raiz do
projeto (documento local, não versionado).

---

## Pré-requisitos

| Ferramenta | Versão | Observação |
|---|---|---|
| Python | **3.10 – 3.12** | Django 5.0.6 **não** roda em 3.13+. |
| PostgreSQL | 14+ | Obrigatório — o `settings.py` fixa o engine `postgresql`. |

> **Windows:** se `python --version` apontar para 3.13/3.14, crie o venv com
> `py -3.12` explicitamente. Depois de ativado, `python` já será o 3.12.

---

## Instalação

Todos os comandos a partir de `gestao-pecuaria/backend/`.

### 1. Ambiente virtual

```bash
py -3.12 -m venv venv
```

Ativar:

```bash
venv\Scripts\Activate.ps1
```

<details>
<summary>Outros shells</summary>

| Shell | Comando |
|---|---|
| PowerShell | `venv\Scripts\Activate.ps1` |
| CMD | `venv\Scripts\activate.bat` |
| Git Bash | `source venv/Scripts/activate` |
| Linux / macOS | `source venv/bin/activate` |

</details>

> Nunca **mova** uma pasta `venv` de lugar — os executáveis dentro de
> `venv/Scripts/` guardam o caminho absoluto do interpretador. Se precisar
> mudar de diretório, apague e recrie.

> **`python -m venv` falha com `WinError 4551`?** É o Smart App Control do
> Windows bloqueando a cópia do `python.exe`. Existe um caminho alternativo
> sem virtualenv, com o atalho `manage.ps1` — veja `ERROS_CONHECIDOS.md`.

### 2. Dependências

```bash
# Desenvolvimento (inclui as de execucao + pytest e pylint):
pip install -r requirements-dev.txt

# Somente execucao, para o servidor:
pip install -r requirements.txt
```

### 3. Variáveis de ambiente

O `settings.py` lê tudo com `python-decouple` **sem valores padrão** — sem o
`.env` o Django nem inicia.

```bash
copy .env.example .env
```

Agora **edite o `.env`**. Os valores herdados do exemplo não funcionam como
estão:

| Variável | O que colocar |
|---|---|
| `SECRET_KEY` | Uma chave gerada (comando abaixo) |
| `DEBUG` | `True` em desenvolvimento |
| `DB_NAME` | Nome do banco — precisa bater com o do passo 4 |
| `DB_USER` | Normalmente `postgres` |
| `DB_PASSWORD` | **A senha real do PostgreSQL** — o exemplo é um placeholder |
| `DB_HOST` / `DB_PORT` | `localhost` / `5432` |

Gerar uma `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Criar o banco

```bash
psql -U postgres -c "CREATE DATABASE gestaopecuariadb;"
```

> **`psql` não é reconhecido?** O instalador do PostgreSQL no Windows não
> adiciona o `bin/` ao PATH. Use o caminho completo, ajustando a versão:
>
> ```bash
> & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "CREATE DATABASE gestaopecuariadb;"
> ```

### 5. Migrações

As migrações **estão versionadas**, então basta aplicá-las:

```bash
python manage.py migrate
```

> Se o banco já existia de uma execução antiga (tabelas presentes, histórico de
> migrações ausente), use `python manage.py migrate --fake-initial`.

### 6. Usuário administrador

```bash
python manage.py createsuperuser
```

Pede **e-mail, nome, CPF e senha** — não pede username, porque o login deste
sistema é por e-mail.

### 7. Subir o servidor

```bash
python manage.py runserver
```

- API: <http://localhost:8000>
- Admin: <http://localhost:8000/admin>

---

## Organização

```
backend/
├── config/                 # projeto Django (settings, urls, wsgi, asgi)
├── apps/
│   ├── autenticacao/       # model Usuario + JWT + perfil + troca de senha
│   └── core/               # produtor → propriedade → gleba → análise →
│                           # recomendação, além de laboratório e cultura
├── staticfiles/            # saída do collectstatic (gerado, não versionar)
├── manage.py
├── requirements.txt        dependencias de execucao
├── requirements-dev.txt    + testes e analise estatica
└── .env.example
```

`apps/` é adicionado ao `sys.path` pelo `config/settings.py`. É por isso que os
imports são `core.*` e `autenticacao.*`, e não `apps.core.*`.

### Modelo de usuário

`autenticacao.Usuario` estende `AbstractUser`, remove o campo `username` e
autentica por **e-mail** (`USERNAME_FIELD = 'email'`). Como o `UserManager`
padrão do Django exige `username`, a app define um `UsuarioManager` próprio —
sem ele o `createsuperuser` quebra.

Campos extras: `nome`, `cpf` (único), `telefone` e `creditos`.

---

## Endpoints

### Autenticação — `/autenticacao/`

| Método | Rota | Descrição |
|---|---|---|
| POST | `/autenticacao/signup/` | Cria usuário |
| POST | `/autenticacao/token/` | Login — retorna `access` e `refresh` |
| POST | `/autenticacao/token/refresh/` | Renova o token de acesso |
| POST | `/autenticacao/logout/` | Invalida o refresh token (blacklist) |
| GET / PUT | `/autenticacao/meuperfil/` | Lê e atualiza o perfil do usuário logado |
| POST | `/autenticacao/alterar-senha/` | Troca de senha |

### Recursos — raiz `/`

CRUD completo (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) via router do DRF:

`/usuarios/` · `/produtores/` · `/propriedades/` · `/glebas/` ·
`/laboratorios/` · `/culturas/` · `/analisesolo/` · `/recomendacoes/`

`/glebas/` aceita `?propriedade=<id>` para listar apenas as glebas de uma
propriedade — é assim que a tela de análise monta a seleção em cascata.

Todos exigem o header `Authorization: Bearer <access_token>` e retornam apenas
os registros do usuário autenticado.

### Tokens

| Token | Validade |
|---|---|
| `access` | 60 minutos |
| `refresh` | 1 dia |

Rotação automática ativada, com o token antigo indo para a blacklist.

---

## Comandos úteis

```bash
python manage.py check
```

```bash
python manage.py makemigrations
```

```bash
python manage.py collectstatic
```

```bash
python manage.py shell
```
