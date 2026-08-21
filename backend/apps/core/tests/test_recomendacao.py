"""
Recomendacao: tudo calculado, nada digitado.

A promessa e que nenhuma dose vem do cliente - todas saem de agronomia.py a
partir do laudo e dos parametros da cultura. Um campo editavel que o servidor
sobrescreve seria apenas uma forma de enganar quem preenche, entao os testes
abaixo tentam justamente enganar: mandam valores absurdos e conferem que foram
ignorados.

Tambem cobre a fronteira declarada do sistema: parametro que falta produz
pendencia explicita, e nao um numero sem lastro.
"""
from decimal import Decimal

import pytest
from rest_framework import status

from core.models import Calcario, Cultura

pytestmark = pytest.mark.django_db


@pytest.fixture
def cultura_parametrizada(cadastros):
    """Cultura com todos os parametros agronomicos preenchidos."""
    cultura = cadastros['cultura']
    cultura.saturacao_bases_desejada = Decimal('70')
    cultura.saturacao_k_desejada = Decimal('4')
    cultura.fosforo_desejado = Decimal('18')
    cultura.fator_fixacao_fosforo = Decimal('5')
    cultura.nitrogenio_recomendado = Decimal('30')
    cultura.enxofre_desejado = Decimal('10')
    cultura.save()
    return cultura


class TestDosesSaoCalculadasEnaoAceitas:
    def test_valores_enviados_pelo_cliente_sao_ignorados(
            self, cliente, analise, cultura_parametrizada, calcario):
        resposta = cliente.post('/recomendacoes/', {
            'analise_solo': analise.pk,
            # Todos absurdos de proposito.
            'kcl': 9999, 'p2o5': 9999, 'n': 9999, 's': 9999, 'gesso': 9999,
            'calcario_calcitico': 9999, 'calcario_dolomitico': 9999,
            'calcario_magnesiano': 9999, 'camada_correcao': 'inventada',
        }, format='json')

        assert resposta.status_code == status.HTTP_201_CREATED
        for campo in ('kcl', 'p2o5', 'n', 's', 'gesso', 'calcario_calcitico',
                      'calcario_dolomitico', 'calcario_magnesiano'):
            assert Decimal(resposta.data[campo]) != Decimal('9999'), campo
        assert resposta.data['camada_correcao'] != 'inventada'

    def test_doses_batem_com_o_calculo_puro(
            self, cliente, analise, cultura_parametrizada, calcario):
        """
        A verdade de referencia vem de agronomia.py, que tem teste proprio com
        valores conferidos a mao. Aqui se verifica o elo: o que a API grava e o
        que o modulo calcula.
        """
        from core.agronomia import recomendacao_completa
        from core.serializers import calcario_para

        esperado = recomendacao_completa(analise, calcario=calcario_para(analise))
        resposta = cliente.post('/recomendacoes/',
                                {'analise_solo': analise.pk}, format='json')

        for campo in ('calcario_calcitico', 'calcario_dolomitico',
                      'calcario_magnesiano', 'gesso', 'kcl', 'p2o5', 'n', 's'):
            gravado = Decimal(resposta.data[campo])
            referencia = Decimal(esperado[campo] if esperado[campo] is not None else 0)
            assert gravado == referencia, campo

    def test_editar_nao_deixa_o_cliente_alterar_dose(
            self, cliente, analise, cultura_parametrizada, calcario):
        criada = cliente.post('/recomendacoes/',
                              {'analise_solo': analise.pk}, format='json').data
        kcl_original = criada['kcl']

        resposta = cliente.put(f"/recomendacoes/{criada['id']}/", {
            'analise_solo': analise.pk, 'kcl': 1,
        }, format='json')

        assert resposta.status_code == status.HTTP_200_OK
        assert resposta.data['kcl'] == kcl_original

    def test_a_calagem_sai_num_unico_campo(
            self, cliente, analise, cultura_parametrizada, calcario):
        # Recomendar tres corretivos para a mesma area nao faria sentido
        # agronomico: dois dos tres ficam zerados.
        dados = cliente.post('/recomendacoes/',
                             {'analise_solo': analise.pk}, format='json').data

        doses = [Decimal(dados[c]) for c in ('calcario_calcitico',
                                             'calcario_dolomitico',
                                             'calcario_magnesiano')]
        assert sum(1 for d in doses if d > 0) <= 1


class TestPendencias:
    def test_cultura_sem_parametros_gera_pendencias(self, cliente, analise):
        # A cultura da fixture nao tem nenhum parametro preenchido.
        dados = cliente.post('/recomendacoes/',
                             {'analise_solo': analise.pk}, format='json').data
        pendencias = dados['memoria_calculo']['pendencias']

        assert pendencias, 'faltando tudo, tem que dizer o que falta'
        assert any('nitrog' in p.lower() for p in pendencias)

    def test_sem_v2_cai_no_metodo_do_aluminio(self, cliente, analise):
        """
        O metodo do aluminio nao depende de parametro por cultura, entao
        funciona mesmo sem V2 cadastrado - e o sistema informa qual usou, em
        vez de simplesmente nao calcular.
        """
        dados = cliente.post('/recomendacoes/',
                             {'analise_solo': analise.pk}, format='json').data
        assert dados['memoria_calculo']['metodo_calagem'] == 'Alumínio e Ca+Mg'
        assert dados['memoria_calculo']['v2_utilizado'] is None

    def test_com_v2_usa_a_saturacao_por_bases(
            self, cliente, analise, cultura_parametrizada):
        dados = cliente.post('/recomendacoes/',
                             {'analise_solo': analise.pk}, format='json').data
        assert dados['memoria_calculo']['metodo_calagem'] == 'Saturação por bases'
        assert Decimal(dados['memoria_calculo']['v2_utilizado']) == Decimal('70.0')

    def test_sem_calcario_cadastrado_a_dose_real_fica_em_aberto(
            self, cliente, analise, cultura_parametrizada):
        # Sem PRNT nao da para converter a necessidade teorica em produto.
        dados = cliente.post('/recomendacoes/',
                             {'analise_solo': analise.pk}, format='json').data
        assert dados['memoria_calculo']['prnt_utilizado'] is None
        assert any('calcário' in p.lower() for p in dados['memoria_calculo']['pendencias'])

    def test_campo_sem_parametro_fica_zerado_e_nao_nulo(self, cliente, analise):
        # O model nao aceita nulo nessas colunas; a pendencia e que explica o
        # zero. Zerar sem explicar seria o problema.
        dados = cliente.post('/recomendacoes/',
                             {'analise_solo': analise.pk}, format='json').data
        assert Decimal(dados['n']) == Decimal('0')
        assert dados['memoria_calculo']['pendencias']


class TestDiagnosticoNaAnalise:
    def test_indices_sao_calculados_a_cada_leitura(self, cliente, analise):
        diagnostico = cliente.get(f'/analisesolo/{analise.pk}/').data['diagnostico']

        # Perfil 'muito acido': V% 15,2 e m% 50,0 (conferidos em test_agronomia)
        assert Decimal(diagnostico['saturacao_bases']) == Decimal('15.2')
        assert Decimal(diagnostico['saturacao_aluminio']) == Decimal('50.0')
        assert diagnostico['classificacao_v'] == 'Muito baixo'

    def test_indice_acompanha_a_correcao_do_valor_de_origem(self, cliente, analise):
        """
        Os indices sao SerializerMethodField e nao colunas. Se fossem gravados,
        corrigir um valor do laudo deixaria o indice defasado apontando para o
        numero antigo - e ninguem notaria.
        """
        antes = cliente.get(f'/analisesolo/{analise.pk}/').data['diagnostico']

        analise.ca = Decimal('4.50')
        analise.save()

        depois = cliente.get(f'/analisesolo/{analise.pk}/').data['diagnostico']
        assert Decimal(depois['saturacao_bases']) > Decimal(antes['saturacao_bases'])

    def test_nao_ha_coluna_de_indice_no_banco(self):
        from core.models import AnaliseSolo
        colunas = {f.name for f in AnaliseSolo._meta.get_fields()}
        assert 'diagnostico' not in colunas
        assert 'saturacao_bases' not in colunas


class TestCamadaDeAmostragem:
    def test_subsuperficie_nao_recebe_calagem(self, cliente, cadastros):
        """
        A formula da calagem e calibrada para 0-20cm. Fora dela o sistema se
        recusa a calcular e diz por que, em vez de dar um numero errado calado.
        """
        from conftest import criar_analise
        funda = criar_analise(cadastros, camada='20-40', laudo='FUNDA')

        dados = cliente.get(f'/analisesolo/{funda.pk}/').data

        assert dados['calagem']['aplicavel'] is False
        assert '20-40' in dados['calagem']['motivo']
        assert dados['recomendacao_previa']['aplicavel'] is False

    def test_superficie_recebe_calagem(self, cliente, analise):
        dados = cliente.get(f'/analisesolo/{analise.pk}/').data
        assert dados['calagem']['aplicavel'] is True


class TestEscolhaDoCalcario:
    def test_prefere_o_de_maior_prnt_do_tipo_indicado(self, cliente, analise, usuario):
        # Ca 0,80 / Mg 0,30 = 2,67 -> calcitico
        Calcario.objects.create(usuario=usuario, nome='Fraco',
                                tipo=Calcario.CALCITICO, prnt='70.00', teor_mgo='2.00')
        forte = Calcario.objects.create(usuario=usuario, nome='Forte',
                                        tipo=Calcario.CALCITICO, prnt='95.00',
                                        teor_mgo='2.00')

        dados = cliente.get(f'/analisesolo/{analise.pk}/').data
        assert dados['calagem']['calcario_sugerido'] == forte.nome

    def test_nao_usa_calcario_de_outra_conta(
            self, cliente, analise, intruso):
        Calcario.objects.create(usuario=intruso, nome='Do intruso',
                                tipo=Calcario.CALCITICO, prnt='99.00', teor_mgo='2.00')

        dados = cliente.get(f'/analisesolo/{analise.pk}/').data
        assert dados['calagem']['calcario_sugerido'] is None

    def test_tipo_divergente_do_teor_de_mgo_e_recusado(self, cliente):
        # A classificacao brasileira separa os tipos pela faixa de MgO, entao
        # divergencia costuma ser erro de digitacao na embalagem.
        resposta = cliente.post('/calcarios/', {
            'nome': 'Incoerente', 'tipo': Calcario.CALCITICO,
            'prnt': '85.00', 'teor_mgo': '20.00',
        }, format='json')

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert 'tipo' in resposta.data
