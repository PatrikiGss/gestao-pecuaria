"""
Django settings para o projeto Gestao Pecuaria.

Gerado por 'django-admin startproject' com Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
import sys
from pathlib import Path
import dj_database_url
from decouple import config, Csv
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

APPS_DIR = os.path.join(BASE_DIR, 'apps')
# Adiciona APPS_DIR no início da lista de caminhos do sistema
sys.path.insert(0, APPS_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# Lista vazia so funciona com DEBUG=True (o Django assume localhost).
# Em producao precisa vir preenchida pelo .env.
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
THIRD_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

PROJECT_APPS = [
    'core.apps.CoreConfig',
    'autenticacao.apps.AutenticacaoConfig',
]

INSTALLED_APPS = PROJECT_APPS + THIRD_APPS + DJANGO_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Serve os estaticos do /admin com DEBUG=False, direto do processo do
    # gunicorn. A posicao nao e preferencia:
    #   - acima do SecurityMiddleware, os estaticos escapariam do
    #     redirecionamento de HTTPS;
    #   - mais abaixo, cada arquivo pagaria o custo dos middlewares de sessao
    #     e autenticacao a toa.
    # Logo depois do SecurityMiddleware e antes de todo o resto e a ordem que
    # a documentacao do whitenoise pede, e a causa mais comum de "instalei e
    # continua sem CSS" e justamente ter posto em outro lugar.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # CorsMiddleware precisa vir antes do CommonMiddleware: se ficar depois,
    # respostas que o CommonMiddleware encerra saem sem os cabecalhos de CORS.
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Duas formas de configurar, e a de producao ganha quando existe.
#
# O provedor gerenciado entrega UMA url:
#   postgresql://usuario:senha@host-pooler.regiao.provedor.tech/banco?sslmode=require
#
# Em desenvolvimento continuam valendo as cinco variaveis separadas do .env.
# Manter os dois caminhos, em vez de migrar tudo para a url, e o que deixa a
# maquina local e a suite de testes intocadas: nada muda aqui enquanto
# DATABASE_URL nao estiver definida.
DATABASE_URL = config('DATABASE_URL', default='')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            # 0 de proposito. O endpoint '-pooler' do provedor JA e um
            # PgBouncer; conexao persistente do Django por cima de um pooler
            # externo segura uma conexao do pool sem usar, em vez de economizar
            # handshake. Com pooler, persistir e o contrario de otimizar.
            conn_max_age=0,
            # O provedor recusa conexao sem TLS. Isto acrescenta
            # OPTIONS={'sslmode': 'require'} mesmo que a url venha sem o
            # parametro na query string.
            ssl_require=True,
            # PgBouncer em modo transacao nao mantem estado entre comandos, e
            # cursor do lado do servidor (o que o .iterator() do Django usa)
            # depende exatamente disso. Nenhuma consulta do projeto usa hoje -
            # mas a falha e do tipo que aparece meses depois, em producao, na
            # primeira listagem grande.
            disable_server_side_cursors=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',#postgresql  sqlite3
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST'),
            'PORT': config('DB_PORT'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Adiciona o modelo customizado de usuário
AUTH_USER_MODEL = 'autenticacao.Usuario'

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

# 'UTC' aqui, com LANGUAGE_CODE pt-br, fazia o servidor ter uma nocao de "hoje"
# diferente da do usuario. Nao aparecia porque a maquina de desenvolvimento
# esta no Brasil e 'date.today()' lia o relogio do sistema; num servidor em UTC
# as duas divergiriam todas as noites, das 21h a meia-noite - e uma analise
# datada de hoje seria recusada como futura, ou vice-versa.
#
# Com USE_TZ=True os datetimes continuam gravados em UTC no banco. Isto aqui
# define apenas como sao interpretados e exibidos - e o que 'timezone.localdate()'
# considera ser hoje.
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
# USE_L10N foi removido no Django 5.0 - a linha nao tinha mais efeito nenhum.
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
# Destino do 'collectstatic' (gerado, nao versionar).
#
# Nao ha STATICFILES_DIRS: o backend e uma API pura, sem nenhum template
# HTML. A pasta 'static/' que existia aqui guardava Bootstrap, jQuery e
# Popper que nada referenciava - o front carrega os proprios via npm.
# Os assets do /admin vem do proprio app do Django.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        # Comprime (gzip/brotli) e poe um hash no nome de cada arquivo, o que
        # permite cache eterno sem risco de servir versao velha.
        #
        # EXIGE que 'collectstatic' tenha rodado: sem o manifesto, qualquer
        # {% static %} levanta ValueError. Por isso o collectstatic e parte do
        # comando de build no servidor, e nao um passo manual.
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CORS Headers Configuration
# CORS_ALLOW_ALL_ORIGINS = True anulava a lista abaixo e liberava qualquer
# origem. A lista fica valendo; para adicionar dominios, use o .env.
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:7777,http://127.0.0.1:7777',
    cast=Csv(),
)

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

#DRF Configuration
REST_FRAMEWORK = {
    # Fechado por padrao. O default era AllowAny, e embora nao houvesse brecha
    # aberta - os nove viewsets declaram IsAuthenticated um por um - a protecao
    # dependia de ninguem esquecer. E a mesma classe de falha do 'validate_campos'
    # que nunca rodava: parecia protegido, e estava, mas por acidente de
    # disciplina e nao por construcao. Com o default invertido, o proximo
    # endpoint que alguem escrever nasce fechado, e abrir passa a ser uma
    # decisao explicita e visivel na revisao.
    #
    # O QUE FICA PUBLICO, E ONDE ISSO ESTA DECLARADO
    #   /autenticacao/signup/          RegisterView, permission_classes=[AllowAny]
    #   /autenticacao/token/           \
    #   /autenticacao/token/refresh/    > TokenViewBase do simplejwt, que declara
    #   /autenticacao/logout/          /  permission_classes = () - tupla vazia,
    #                                     entao nao consulta este default.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # Toda listagem passa a vir paginada. Ver config/paginacao.py.
    'DEFAULT_PAGINATION_CLASS': 'config.paginacao.PaginacaoPadrao',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ],
    # Traduz o ProtectedError do on_delete=PROTECT em 409 com explicacao, em
    # vez do 500 sem mensagem que o DRF devolveria. Ver config/excecoes.py.
    'EXCEPTION_HANDLER': 'config.excecoes.manipulador_de_excecoes',
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # O tempo de vida do token de acesso
    # Rede de seguranca do servidor para a inatividade.
    #
    # A regra de "sair depois de 1h parado" e aplicada no navegador
    # (src/inatividade.js), porque so o cliente sabe se houve interacao. Mas
    # regra que so existe no cliente nao vale nada contra um token copiado:
    # bastava guardar o refresh e usa-lo no dia seguinte, ja que a vida dele
    # era de 1 DIA. Agora o servidor tambem recusa.
    #
    # 2h, e nao 1h, de proposito: com ROTATE_REFRESH_TOKENS cada chamada a API
    # renova a contagem, entao a janela so se esgota sem uso. A folga cobre o
    # caso de alguem ativo por muito tempo numa tela sem chamar a API (um
    # formulario longo de analise, por exemplo) - com 1h exato, esse usuario
    # seria deslogado ao salvar, apesar de nunca ter ficado parado.
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=2),
    'ROTATE_REFRESH_TOKENS': True,  # Gira os tokens de refresh automaticamente
    'BLACKLIST_AFTER_ROTATION': True,  # Coloca o token antigo na lista negra
    'ALGORITHM': 'HS256',  # Algoritmo de criptografia
    'SIGNING_KEY': SECRET_KEY,  # Usa a chave secreta definida anteriormente
    'AUTH_HEADER_TYPES': ('Bearer',),  # Tipo de cabeçalho de autenticação
    'TOKEN_USER_CLASS': 'autenticacao.Usuario',  # O modelo de usuário que será autenticado
    # 'TOKEN_BLACKLIST_ENABLED' nao existe no simplejwt e era ignorado. A
    # blacklist ja esta ativa por 'rest_framework_simplejwt.token_blacklist'
    # estar em INSTALLED_APPS.
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),  # Para tokens deslizantes, caso use
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# HTTPS
#
# Tudo neste bloco vale SO com DEBUG=False. Ligado em desenvolvimento, quebra o
# localhost: o SECURE_SSL_REDIRECT manda o navegador para
# https://localhost:8000, que nao existe. E por isso que ele esta dentro de um
# 'if' em vez de solto no arquivo.
#
# Sao os quatro avisos que 'manage.py check --deploy' aponta, mais a linha do
# proxy - que nao e aviso, e pre-requisito das outras.
if not DEBUG:
    # A plataforma encerra o TLS no proxy e entrega a requisicao em HTTP para a
    # aplicacao. Sem esta linha o Django acha que TODA conexao e insegura - e o
    # SECURE_SSL_REDIRECT logo abaixo vira um LACO INFINITO: o Django manda
    # para https, o proxy repassa em http, o Django manda para https de novo.
    # E o erro que mais confunde neste deploy, porque o sintoma
    # (ERR_TOO_MANY_REDIRECTS) nao aponta para a causa.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    SECURE_SSL_REDIRECT = True      # security.W008
    SESSION_COOKIE_SECURE = True    # security.W012
    CSRF_COOKIE_SECURE = True       # security.W016

    # security.W004. Comeca em 1h de proposito.
    #
    # O HSTS fica GRAVADO no navegador pelo tempo que voce disser, e nao ha
    # como cancelar do lado do servidor. Publicar 31536000 (1 ano) por engano
    # num dominio que depois precise responder em HTTP deixa o site
    # inacessivel por um ano nos navegadores que ja visitaram. Suba para
    # 31536000 pela variavel de ambiente depois de uma semana no ar sem
    # problema - nao precisa mexer neste arquivo para isso.
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=3600, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True