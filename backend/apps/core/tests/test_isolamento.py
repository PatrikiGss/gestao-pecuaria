"""
Isolamento entre contas.

O sistema promete que cada conta enxerga apenas os proprios dados, e essa
promessa se apoia em tres camadas independentes:

    get_queryset      filtra a LEITURA
    perform_create    carimba o dono na ESCRITA
    DonoDoRecursoMixin restringe as opcoes de CHAVE ESTRANGEIRA

O defeito nº 4 da auditoria vivia justamente na terceira: existiam
'validate_campos' e 'validate_analise', nomeados a partir de campos
inexistentes, entao o DRF nunca os executava. Codigo morto com aparencia de
protecao - passava em revisao porque a funcao estava la, escrita e plausivel.

Por isso cada teste aqui usa DUAS contas. Com uma so, todos passariam mesmo
se o filtro por dono nao existisse.
"""
import pytest
from rest_framework import status

from core.models import AnaliseSolo, Cultura, Gleba, Laboratorio, Produtor

pytestmark = pytest.mark.django_db


# ==========================================================================
# Leitura
# ==========================================================================

class TestListagemNaoVazaEntreContas:
    @pytest.mark.parametrize('rota, chave', [
        ('/produtores/', 'produtor'),
        ('/propriedades/', 'propriedade'),
        ('/glebas/', 'gleba'),
        ('/laboratorios/', 'laboratorio'),
        ('/culturas/', 'cultura'),
    ])
    def test_listagem_so_traz_o_que_e_do_dono(
            self, cliente, cadastros, cadastros_intruso, rota, chave):
        resposta = cliente.get(rota)
        ids = [linha['id'] for linha in resposta.data['results']]

        assert resposta.status_code == status.HTTP_200_OK
        assert cadastros[chave].pk in ids
        assert cadastros_intruso[chave].pk not in ids

    def test_analises_de_outra_conta_nao_aparecem(
            self, cliente, analise, cadastros_intruso):
        from conftest import criar_analise
        alheia = criar_analise(cadastros_intruso, laudo='LAUDO-DO-INTRUSO')

        resposta = cliente.get('/analisesolo/')
        ids = [linha['id'] for linha in resposta.data['results']]

        assert analise.pk in ids
        assert alheia.pk not in ids

    def test_usuarios_lista_apenas_a_propria_conta(self, cliente, usuario, intruso):
        # A listagem de usuarios devolve o proprio registro e nada mais - nem
        # os e-mails das outras contas.
        resposta = cliente.get('/usuarios/')
        assert [u['id'] for u in resposta.data['results']] == [usuario.pk]


class TestAcessoDiretoPorId:
    def test_detalhe_de_registro_alheio_da_404(self, cliente, cadastros_intruso):
        # 404 e nao 403, de proposito: 403 confirmaria que o id existe.
        resposta = cliente.get(f"/produtores/{cadastros_intruso['produtor'].pk}/")
        assert resposta.status_code == status.HTTP_404_NOT_FOUND

    def test_nao_da_para_editar_registro_alheio(self, cliente, cadastros_intruso):
        alvo = cadastros_intruso['cultura']
        resposta = cliente.patch(f'/culturas/{alvo.pk}/', {'nome': 'Sequestrada'}, format='json')

        assert resposta.status_code == status.HTTP_404_NOT_FOUND
        alvo.refresh_from_db()
        assert alvo.nome != 'Sequestrada'

    def test_nao_da_para_excluir_registro_alheio(self, cliente, cadastros_intruso):
        alvo = cadastros_intruso['laboratorio']
        resposta = cliente.delete(f'/laboratorios/{alvo.pk}/')

        assert resposta.status_code == status.HTTP_404_NOT_FOUND
        assert Laboratorio.objects.filter(pk=alvo.pk).exists()


# ==========================================================================
# Escrita: o IDOR do defeito nº 4
# ==========================================================================

class TestNaoDaParaApontarParaRecursoAlheio:
    def test_analise_em_gleba_de_outra_conta_e_recusada(
            self, cliente, cadastros, cadastros_intruso):
        """
        O caso exato do defeito nº 4: criar uma analise propria apontando para
        a gleba de outro usuario. A leitura estava protegida, a escrita nao.
        """
        payload = {
            'laboratorio': cadastros['laboratorio'].pk,
            'gleba': cadastros_intruso['gleba'].pk,        # <- de outra conta
            'cultura': cadastros['cultura'].pk,
            'data': '2024-05-10', 'camada': '0-20', 'area': '10.00',
            'laudo': 'L-1', 'ph_h2o': '5.5', 's': '8', 'p': '6', 'k': '0.15',
            'ca': '2.4', 'mg': '0.9', 'na': '0.02', 'al': '0.3', 'h': '3.5',
            'materia_organica': '2.8', 'areia': '40', 'silte': '25',
            'argila': '35', 'mn': '8', 'fe': '30', 'cu': '1.2', 'zn': '2.1',
            'b': '0.3',
        }
        resposta = cliente.post('/analisesolo/', payload, format='json')

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert 'gleba' in resposta.data
        assert not AnaliseSolo.objects.filter(laudo='L-1').exists()

    def test_propriedade_em_produtor_de_outra_conta_e_recusada(
            self, cliente, cadastros_intruso):
        resposta = cliente.post('/propriedades/', {
            'produtor': cadastros_intruso['produtor'].pk,
            'nome': 'Invasora', 'longitude': '-50.3', 'latitude': '-27.8',
            'endereco': 'x', 'cidade': 'Lages', 'estado': 'SC',
        }, format='json')

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert 'produtor' in resposta.data

    def test_gleba_em_propriedade_de_outra_conta_e_recusada(
            self, cliente, cadastros_intruso):
        resposta = cliente.post('/glebas/', {
            'propriedade': cadastros_intruso['propriedade'].pk, 'nome': 'Invasora',
        }, format='json')

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert 'propriedade' in resposta.data

    def test_recomendacao_sobre_analise_de_outra_conta_e_recusada(
            self, cliente, cadastros_intruso):
        from conftest import criar_analise
        alheia = criar_analise(cadastros_intruso)

        resposta = cliente.post('/recomendacoes/',
                                {'analise_solo': alheia.pk}, format='json')

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert 'analise_solo' in resposta.data


class TestDonoEhCarimbadoPeloServidor:
    def test_produtor_nasce_do_usuario_da_requisicao(self, cliente, usuario, intruso):
        # Mesmo mandando 'usuario' no corpo, o servidor ignora e usa o da sessao.
        resposta = cliente.post('/produtores/', {
            'usuario': intruso.pk,
            'cpf': '52998224725', 'nome': 'Novo', 'telefone': '4899990000',
            'email': 'novo@exemplo.com',
        }, format='json')

        assert resposta.status_code == status.HTTP_201_CREATED
        assert Produtor.objects.get(pk=resposta.data['id']).usuario_id == usuario.pk


# ==========================================================================
# Unicidade por usuario, e nao global
# ==========================================================================

class TestUnicidadePorUsuario:
    """
    Antes as restricoes eram globais, e o primeiro usuario a cadastrar um CPF
    bloqueava todos os outros - dois tecnicos nao podiam atender o mesmo
    produtor. A unicidade passou a ser composta com o dono.
    """

    def test_duas_contas_podem_cadastrar_o_mesmo_cpf(
            self, cliente, cliente_intruso):
        dados = {'cpf': '52998224725', 'nome': 'Produtor Compartilhado',
                 'telefone': '4899990000', 'email': 'p@exemplo.com'}

        assert cliente.post('/produtores/', dados, format='json').status_code == 201
        assert cliente_intruso.post('/produtores/', dados, format='json').status_code == 201

    def test_a_mesma_conta_nao_repete_o_cpf(self, cliente):
        dados = {'cpf': '52998224725', 'nome': 'Produtor', 'telefone': '4899990000',
                 'email': 'p@exemplo.com'}
        assert cliente.post('/produtores/', dados, format='json').status_code == 201

        segunda = cliente.post('/produtores/', dict(dados, email='outro@exemplo.com'),
                               format='json')
        assert segunda.status_code == status.HTTP_400_BAD_REQUEST

    def test_duas_contas_podem_ter_cultura_de_mesmo_nome(
            self, cliente, cliente_intruso):
        assert cliente.post('/culturas/', {'nome': 'Soja'}, format='json').status_code == 201
        assert cliente_intruso.post('/culturas/', {'nome': 'Soja'},
                                    format='json').status_code == 201

    def test_nome_de_cultura_nao_repete_nem_trocando_maiusculas(self, cliente):
        assert cliente.post('/culturas/', {'nome': 'Soja'}, format='json').status_code == 201

        resposta = cliente.post('/culturas/', {'nome': 'SOJA'}, format='json')
        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert Cultura.objects.filter(nome__iexact='soja').count() == 1

    def test_espacos_extras_nao_furam_a_unicidade(self, cliente):
        assert cliente.post('/culturas/', {'nome': 'Cana de acucar'},
                            format='json').status_code == 201

        resposta = cliente.post('/culturas/', {'nome': '  Cana   de acucar  '},
                                format='json')
        assert resposta.status_code == status.HTTP_400_BAD_REQUEST

    def test_gleba_repetida_na_mesma_propriedade_e_recusada(self, cliente, cadastros):
        resposta = cliente.post('/glebas/', {
            'propriedade': cadastros['propriedade'].pk,
            'nome': cadastros['gleba'].nome.lower(),
        }, format='json')

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert 'nome' in resposta.data

    def test_mesma_gleba_pode_existir_em_propriedades_diferentes(
            self, cliente, cadastros):
        from core.models import Propriedade
        outra = Propriedade.objects.create(
            produtor=cadastros['produtor'], nome='Segunda Fazenda',
            longitude='-50.4', latitude='-27.9', endereco='y',
            cidade='Lages', estado='SC')

        resposta = cliente.post('/glebas/', {
            'propriedade': outra.pk, 'nome': cadastros['gleba'].nome,
        }, format='json')

        assert resposta.status_code == status.HTTP_201_CREATED
        assert Gleba.objects.filter(nome=cadastros['gleba'].nome).count() == 2
