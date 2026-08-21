"""
Exclusao: o que pode ser apagado, e o que leva o historico junto.

A analise de solo e o registro historico do sistema. Apagar um cadastro
auxiliar nunca deve destrui-la - e a protecao precisa valer por TODOS os
caminhos, nao so pelo mais obvio.

Ate pouco tempo valia pela metade, de um jeito que enganava: a tela recusava
apagar a gleba explicando que havia analises vinculadas, mas apagar o
laboratorio que fez essas mesmas analises destruia todas elas em silencio, com
a interface confirmando sucesso. O caminho bloqueado e o caminho aberto
levavam exatamente as mesmas linhas.

E o tipo de falha que nenhuma ferramenta estatica encontra: 'CASCADE' e um
valor valido, o codigo compila, o lint passa, e a consequencia so aparece
quando alguem clica no botao errado - momento em que ja nao ha o que fazer.
"""
import pytest
from rest_framework import status

from core.models import AnaliseSolo, Cultura, Gleba, Laboratorio, Recomendacao

pytestmark = pytest.mark.django_db


class TestExclusaoBloqueadaPorAnalise:
    """Nenhum destes tres caminhos pode levar uma analise junto."""

    @pytest.mark.parametrize('rota, chave', [
        ('/laboratorios/', 'laboratorio'),
        ('/culturas/', 'cultura'),
        ('/glebas/', 'gleba'),
    ])
    def test_recusa_com_409_e_preserva_a_analise(
            self, cliente, cadastros, analise, rota, chave):
        alvo = cadastros[chave]

        resposta = cliente.delete(f'/{rota.strip("/")}/{alvo.pk}/')

        assert resposta.status_code == status.HTTP_409_CONFLICT
        # A analise continua la - que e o ponto de tudo isto.
        assert AnaliseSolo.objects.filter(pk=analise.pk).exists()

    @pytest.mark.parametrize('rota, chave', [
        ('/laboratorios/', 'laboratorio'),
        ('/culturas/', 'cultura'),
        ('/glebas/', 'gleba'),
    ])
    def test_a_mensagem_diz_o_que_esta_no_caminho(
            self, cliente, cadastros, analise, rota, chave):
        # 409 sem explicacao deixaria o usuario sem saber o que fazer. A
        # mensagem precisa nomear o obstaculo e quantos sao.
        resposta = cliente.delete(f'/{rota.strip("/")}/{cadastros[chave].pk}/')
        detalhe = resposta.data['detail']

        assert 'análise de solo' in detalhe
        assert '1 ' in detalhe

    def test_contagem_no_plural_quando_ha_varias(self, cliente, cadastros, analise):
        from conftest import criar_analise
        criar_analise(cadastros, laudo='LAUDO-002')
        criar_analise(cadastros, laudo='LAUDO-003')

        resposta = cliente.delete(f"/laboratorios/{cadastros['laboratorio'].pk}/")

        assert '3 análises de solo' in resposta.data['detail']
        assert 'dependem' in resposta.data['detail']

    def test_produtor_com_historico_tambem_e_bloqueado(
            self, cliente, cadastros, analise):
        # Produtor -> Propriedade -> Gleba sao CASCADE entre si, mas a analise
        # trava a gleba com PROTECT. O Django percorre a cascata inteira antes
        # de apagar, encontra a protecao no fim e recusa a operacao toda.
        resposta = cliente.delete(f"/produtores/{cadastros['produtor'].pk}/")

        assert resposta.status_code == status.HTTP_409_CONFLICT
        assert AnaliseSolo.objects.filter(pk=analise.pk).exists()
        assert Gleba.objects.filter(pk=cadastros['gleba'].pk).exists()


class TestExclusaoPermitidaQuandoNadaDepende:
    """
    O outro lado: proteger demais tambem e defeito. Cadastro sem vinculo tem
    que continuar podendo ser apagado, senao a tela vira um deposito.
    """

    def test_laboratorio_sem_analise_e_excluido(self, cliente, usuario):
        livre = Laboratorio.objects.create(
            usuario=usuario, nome='Sem vinculo', endereco='r', cidade='Lages',
            estado='SC', telefone='4933331111', email='livre@exemplo.com')

        resposta = cliente.delete(f'/laboratorios/{livre.pk}/')

        assert resposta.status_code == status.HTTP_204_NO_CONTENT
        assert not Laboratorio.objects.filter(pk=livre.pk).exists()

    def test_cultura_sem_analise_e_excluida(self, cliente, usuario):
        livre = Cultura.objects.create(usuario=usuario, nome='Sem vinculo')

        assert cliente.delete(f'/culturas/{livre.pk}/').status_code == 204
        assert not Cultura.objects.filter(pk=livre.pk).exists()

    def test_gleba_sem_analise_e_excluida(self, cliente, cadastros):
        livre = Gleba.objects.create(
            propriedade=cadastros['propriedade'], nome='Talhao vazio')

        assert cliente.delete(f'/glebas/{livre.pk}/').status_code == 204
        assert not Gleba.objects.filter(pk=livre.pk).exists()

    def test_apagar_a_analise_libera_o_cadastro(self, cliente, cadastros, analise):
        # A ordem funciona: removida a analise, o laboratorio sai.
        assert cliente.delete(f"/laboratorios/{cadastros['laboratorio'].pk}/").status_code == 409

        AnaliseSolo.objects.filter(pk=analise.pk).delete()

        assert cliente.delete(f"/laboratorios/{cadastros['laboratorio'].pk}/").status_code == 204


class TestCascataDesejada:
    """
    Nem toda cascata e problema. A recomendacao e derivada da analise: sem ela
    nao significa nada, entao acompanhar a exclusao e o comportamento correto.
    """

    def test_recomendacao_acompanha_a_analise(self, cliente, analise):
        resposta = cliente.post('/recomendacoes/',
                                {'analise_solo': analise.pk}, format='json')
        assert resposta.status_code == status.HTTP_201_CREATED
        recomendacao_id = resposta.data['id']

        AnaliseSolo.objects.filter(pk=analise.pk).delete()

        assert not Recomendacao.objects.filter(pk=recomendacao_id).exists()
