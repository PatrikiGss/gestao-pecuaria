"""
Conta: senha, privilegio e sessao.

Estes sao os defeitos criticos 1, 2, 3 e 5 da auditoria. Todos vinham da mesma
origem - 'fields = "__all__"' num ModelSerializer de usuario - e todos tem em
comum passar despercebidos: a aplicacao funciona igual com ou sem eles. Contas
eram criadas, listadas e editadas normalmente enquanto a senha ia crua para o
banco e qualquer POST anonimo podia declarar 'is_superuser'.
"""
import pytest
from django.contrib.auth.hashers import identify_hasher
from rest_framework import status

from autenticacao.models import CREDITOS_INICIAIS, Usuario

pytestmark = pytest.mark.django_db

SENHA_BOA = 'Solo!Forte#2024'

CADASTRO = {
    'nome': 'Novo Tecnico',
    'email': 'novo@exemplo.com',
    'cpf': '52998224725',
    'telefone': '4899990000',
    'password': SENHA_BOA,
}


# ==========================================================================
# Defeito 1: senha em texto puro
# ==========================================================================

class TestSenhaEhArmazenadaComHash:
    def test_cadastro_publico_grava_hash(self, anonimo):
        resposta = anonimo.post('/autenticacao/signup/', CADASTRO, format='json')
        assert resposta.status_code == status.HTTP_201_CREATED

        usuario = Usuario.objects.get(email=CADASTRO['email'])
        assert usuario.password != SENHA_BOA
        # identify_hasher levanta se a string nao for um hash reconhecido.
        assert identify_hasher(usuario.password) is not None
        assert usuario.check_password(SENHA_BOA)

    def test_conta_criada_pela_api_consegue_autenticar(self, anonimo):
        # O sintoma pratico do defeito: sem set_password a senha ia crua, e o
        # login depois falhava porque o hash conferido nunca batia.
        anonimo.post('/autenticacao/signup/', CADASTRO, format='json')

        token = anonimo.post('/autenticacao/token/', {
            'email': CADASTRO['email'], 'password': SENHA_BOA,
        }, format='json')

        assert token.status_code == status.HTTP_200_OK
        assert 'access' in token.data and 'refresh' in token.data

    def test_usuarios_endpoint_tambem_aplica_hash(self, cliente):
        resposta = cliente.post('/usuarios/', dict(CADASTRO, email='outro@exemplo.com',
                                                   cpf='15350946056'), format='json')
        assert resposta.status_code == status.HTTP_201_CREATED
        assert Usuario.objects.get(email='outro@exemplo.com').check_password(SENHA_BOA)

    @pytest.mark.parametrize('fraca', ['123', 'senha', '12345678', 'password'])
    def test_senha_fraca_e_recusada(self, anonimo, fraca):
        resposta = anonimo.post('/autenticacao/signup/',
                                dict(CADASTRO, password=fraca), format='json')
        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in resposta.data


# ==========================================================================
# Defeito 2: password exposto na leitura
# ==========================================================================

class TestSenhaNuncaSaiNaResposta:
    def test_cadastro_nao_devolve_o_campo(self, anonimo):
        resposta = anonimo.post('/autenticacao/signup/', CADASTRO, format='json')
        assert 'password' not in resposta.data

    def test_listagem_de_usuarios_nao_devolve_o_campo(self, cliente):
        resposta = cliente.get('/usuarios/')
        for linha in resposta.data['results']:
            assert 'password' not in linha

    def test_perfil_nao_devolve_o_campo(self, cliente):
        assert 'password' not in cliente.get('/autenticacao/meuperfil/').data


# ==========================================================================
# Defeito 3: escalonamento de privilegio
# ==========================================================================

class TestNaoDaParaSeTornarAdministrador:
    @pytest.mark.parametrize('campo', ['is_superuser', 'is_staff'])
    def test_cadastro_publico_ignora_o_campo(self, anonimo, campo):
        """
        A rota de cadastro e AllowAny de proposito. Se o serializer aceitasse
        estes campos, um POST anonimo criaria um administrador.
        """
        resposta = anonimo.post('/autenticacao/signup/',
                                dict(CADASTRO, **{campo: True}), format='json')

        assert resposta.status_code == status.HTTP_201_CREATED
        assert getattr(Usuario.objects.get(email=CADASTRO['email']), campo) is False

    @pytest.mark.parametrize('campo', ['is_superuser', 'is_staff'])
    def test_edicao_do_proprio_registro_ignora_o_campo(self, cliente, usuario, campo):
        cliente.patch(f'/usuarios/{usuario.pk}/', {campo: True}, format='json')

        usuario.refresh_from_db()
        assert getattr(usuario, campo) is False

    def test_creditos_sao_somente_leitura(self, cliente, usuario):
        # 'creditos' e exibido mas nao aceito na entrada: antes o proprio
        # usuario editava o proprio saldo.
        cliente.patch(f'/usuarios/{usuario.pk}/', {'creditos': 999999}, format='json')

        usuario.refresh_from_db()
        assert usuario.creditos == CREDITOS_INICIAIS

    def test_creditos_no_cadastro_tambem_sao_ignorados(self, anonimo):
        anonimo.post('/autenticacao/signup/', dict(CADASTRO, creditos=999999),
                     format='json')
        assert Usuario.objects.get(email=CADASTRO['email']).creditos == CREDITOS_INICIAIS


# ==========================================================================
# Defeito 5: logout que nao deslogava, e troca de senha
# ==========================================================================

class TestTrocaDeSenha:
    def test_troca_com_a_senha_atual_correta(self, cliente):
        resposta = cliente.post('/autenticacao/alterar-senha/', {
            'old_password': SENHA_BOA, 'new_password': 'Nova!Senha#2024',
        }, format='json')
        assert resposta.status_code == status.HTTP_200_OK

    def test_senha_atual_errada_e_recusada(self, cliente):
        resposta = cliente.post('/autenticacao/alterar-senha/', {
            'old_password': 'chute', 'new_password': 'Nova!Senha#2024',
        }, format='json')
        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert 'old_password' in resposta.data

    def test_nova_senha_fraca_e_recusada(self, cliente):
        # Os validadores de AUTH_PASSWORD_VALIDATORS so rodam quando chamados
        # explicitamente: sem isso a API aceitava trocar a senha por "123".
        resposta = cliente.post('/autenticacao/alterar-senha/', {
            'old_password': SENHA_BOA, 'new_password': '123',
        }, format='json')
        assert resposta.status_code == status.HTTP_400_BAD_REQUEST

    def test_nova_senha_igual_a_atual_e_recusada(self, cliente):
        resposta = cliente.post('/autenticacao/alterar-senha/', {
            'old_password': SENHA_BOA, 'new_password': SENHA_BOA,
        }, format='json')
        assert resposta.status_code == status.HTTP_400_BAD_REQUEST

    def test_trocar_a_senha_invalida_as_sessoes_abertas(self, usuario, anonimo):
        """
        Sem isto, trocar a senha nao expulsava ninguem: uma sessao aberta antes
        da troca continuava valida ate o refresh token vencer - que era o unico
        motivo de alguem trocar a senha as pressas.
        """
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

        tokens = anonimo.post('/autenticacao/token/', {
            'email': usuario.email, 'password': SENHA_BOA,
        }, format='json').data

        logado = APIClient()
        logado.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        logado.post('/autenticacao/alterar-senha/', {
            'old_password': SENHA_BOA, 'new_password': 'Nova!Senha#2024',
        }, format='json')

        # O refresh que a sessao guardava nao serve mais.
        assert BlacklistedToken.objects.filter(token__user=usuario).exists()
        renovacao = anonimo.post('/autenticacao/token/refresh/',
                                 {'refresh': tokens['refresh']}, format='json')
        assert renovacao.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    def test_logout_manda_o_refresh_para_a_blacklist(self, usuario, anonimo):
        # O logout so apagava o token do navegador: o refresh continuava valido
        # no servidor por um dia, e o endpoint de blacklist nunca era chamado.
        tokens = anonimo.post('/autenticacao/token/', {
            'email': usuario.email, 'password': SENHA_BOA,
        }, format='json').data

        assert anonimo.post('/autenticacao/logout/',
                            {'refresh': tokens['refresh']}, format='json').status_code == 200

        depois = anonimo.post('/autenticacao/token/refresh/',
                              {'refresh': tokens['refresh']}, format='json')
        assert depois.status_code == status.HTTP_401_UNAUTHORIZED


class TestVidaDosTokens:
    def test_refresh_dura_bem_menos_que_um_dia(self):
        """
        A vida do refresh era de 1 DIA, e era por isso que a sessao nunca
        expirava: o access de 60min vencia e a renovacao seguia em silencio.
        """
        from datetime import timedelta

        from django.conf import settings

        assert settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] <= timedelta(hours=3)
        assert settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS'] is True
        assert settings.SIMPLE_JWT['BLACKLIST_AFTER_ROTATION'] is True


# ==========================================================================
# Superficie publica da API
# ==========================================================================

class TestSuperficiePublica:
    @pytest.mark.parametrize('rota', [
        '/', '/produtores/', '/propriedades/', '/glebas/', '/laboratorios/',
        '/culturas/', '/calcarios/', '/analisesolo/', '/recomendacoes/',
        '/usuarios/', '/autenticacao/meuperfil/', '/autenticacao/alterar-senha/',
    ])
    def test_rota_fechada_recusa_anonimo(self, anonimo, rota):
        """
        O default do DRF era AllowAny. Nao havia brecha aberta - os nove
        viewsets declaravam IsAuthenticated um por um - mas a protecao dependia
        de ninguem esquecer. Este teste passa a cobrar a lista inteira.
        """
        resposta = anonimo.get(rota)
        assert resposta.status_code in (status.HTTP_401_UNAUTHORIZED,
                                        status.HTTP_403_FORBIDDEN)

    def test_o_default_do_drf_e_fechado(self):
        # A garantia estrutural: uma view nova que esqueca de declarar
        # permission_classes nasce fechada.
        from django.conf import settings
        assert settings.REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] == [
            'rest_framework.permissions.IsAuthenticated'
        ]

    @pytest.mark.parametrize('rota', [
        '/autenticacao/signup/', '/autenticacao/token/',
        '/autenticacao/token/refresh/', '/autenticacao/logout/',
    ])
    def test_rota_publica_continua_alcancavel(self, anonimo, rota):
        # O outro lado: fechar demais quebraria o login. 400 significa que a
        # requisicao passou pela permissao e chegou na validacao.
        resposta = anonimo.post(rota, {}, format='json')
        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
