"""
Listagem: paginacao, filtros e CUSTO EM CONSULTAS.

O teste de contagem de consultas e o mais importante deste arquivo, e o motivo
merece ser dito: um select_related removido por engano NAO QUEBRA NADA. A
resposta continua correta, os testes de conteudo continuam verdes, o lint nao
reclama - a pagina so fica lenta, em silencio, e o custo cresce com o tamanho
do historico.

Foi exatamente o que aconteceu: uma pagina de 20 analises custava 62 consultas,
cerca de 3 por linha, porque 'calcario_para' ia ao banco a cada chamada e era
chamada duas vezes por linha. A paginacao tinha sido introduzida justamente
para o custo nao crescer com o historico, mas o custo POR PAGINA continuava
proporcional ao numero de linhas.

Depois da correcao sao 3 consultas, independentemente de quantas linhas vem.
Os testes abaixo comparam o custo de UMA linha com o de MUITAS: se a diferenca
for maior que zero, o N+1 voltou. Fixar o numero absoluto seria fragil (um
campo novo pode mudar a linha de base de forma legitima); o que nao pode mudar
e a INCLINACAO.
"""
import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def muitas_analises(cadastros, calcario):
    """Doze analises na mesma conta, com datas e culturas variadas."""
    from conftest import criar_analise
    from core.models import Cultura

    outra_cultura = Cultura.objects.create(usuario=cadastros['cultura'].usuario,
                                           nome='Milho')
    analises = []
    for i in range(12):
        analises.append(criar_analise(
            cadastros,
            laudo=f'LAUDO-{i:03d}',
            data=f'2024-{(i % 12) + 1:02d}-15',
            cultura=cadastros['cultura'] if i % 2 else outra_cultura,
        ))
    return analises


def contar_consultas(cliente, rota, **params):
    with CaptureQueriesContext(connection) as ctx:
        resposta = cliente.get(rota, params)
    assert resposta.status_code == status.HTTP_200_OK
    return len(ctx.captured_queries), resposta


# ==========================================================================
# Custo em consultas
# ==========================================================================

class TestCustoNaoCresceComAsLinhas:
    def test_analises_custam_o_mesmo_com_1_e_com_12_linhas(
            self, cliente, muitas_analises):
        uma, r1 = contar_consultas(cliente, '/analisesolo/', page_size=1)
        doze, r12 = contar_consultas(cliente, '/analisesolo/', page_size=12)

        assert len(r1.data['results']) == 1
        assert len(r12.data['results']) == 12
        assert doze == uma, (
            f'N+1 de volta: 1 linha custou {uma} consultas e 12 custaram {doze}. '
            f'A diferenca de {doze - uma} cresce com o historico.'
        )

    def test_recomendacoes_custam_o_mesmo_com_1_e_com_muitas(
            self, cliente, muitas_analises):
        for analise in muitas_analises[:6]:
            cliente.post('/recomendacoes/', {'analise_solo': analise.pk}, format='json')

        uma, _ = contar_consultas(cliente, '/recomendacoes/', page_size=1)
        seis, r = contar_consultas(cliente, '/recomendacoes/', page_size=6)

        assert len(r.data['results']) == 6
        assert seis == uma, (
            f'N+1 de volta em /recomendacoes/: {uma} para 1 linha, {seis} para 6.'
        )

    def test_o_teto_de_consultas_da_pagina(self, cliente, muitas_analises):
        """
        Um limite absoluto, alem da inclinacao. Hoje sao 3: a contagem da
        paginacao, a pagina em si, e os calcarios do usuario (carregados uma
        vez). Se este numero subir, alguem acrescentou uma consulta por
        requisicao - o que pode ser legitimo, mas merece ser notado.
        """
        consultas, _ = contar_consultas(cliente, '/analisesolo/', page_size=12)
        assert consultas <= 4, f'{consultas} consultas para montar uma pagina'

    def test_calcarios_sao_carregados_uma_vez_e_nao_por_linha(
            self, cliente, muitas_analises, calcario):
        """
        'calagem' e 'recomendacao_previa' pedem o calcario indicado na MESMA
        linha. Sem cache por requisicao seriam duas consultas por analise.
        """
        consultas, resposta = contar_consultas(cliente, '/analisesolo/', page_size=12)

        # A prova de que o calcario foi de fato resolvido, e nao pulado.
        assert resposta.data['results'][0]['calagem']['calcario_sugerido'] == calcario.nome
        assert consultas <= 4


# ==========================================================================
# Paginacao
# ==========================================================================

class TestPaginacao:
    def test_resposta_tem_a_forma_paginada(self, cliente, muitas_analises):
        dados = cliente.get('/analisesolo/').data
        assert set(dados) >= {'count', 'next', 'previous', 'results'}
        assert dados['count'] == 12

    def test_page_size_respeita_o_pedido(self, cliente, muitas_analises):
        assert len(cliente.get('/analisesolo/', {'page_size': 5}).data['results']) == 5

    def test_page_size_tem_teto(self, cliente, muitas_analises):
        # Sem teto, '?page_size=999999' devolveria a colecao inteira e anularia
        # o motivo de haver paginacao.
        from config.paginacao import PaginacaoPadrao
        resposta = cliente.get('/analisesolo/', {'page_size': 999999})
        assert len(resposta.data['results']) <= PaginacaoPadrao.max_page_size

    def test_paginas_nao_repetem_nem_pulam_registros(self, cliente, muitas_analises):
        """
        Paginacao sobre queryset sem ordenacao estavel embaralha entre paginas:
        o mesmo registro aparece duas vezes e outro some. So se ve conferindo
        as paginas juntas.
        """
        p1 = cliente.get('/analisesolo/', {'page_size': 5, 'page': 1}).data['results']
        p2 = cliente.get('/analisesolo/', {'page_size': 5, 'page': 2}).data['results']
        p3 = cliente.get('/analisesolo/', {'page_size': 5, 'page': 3}).data['results']

        ids = [x['id'] for x in p1 + p2 + p3]
        assert len(ids) == 12
        assert len(set(ids)) == 12, 'ha registro repetido entre paginas'

    def test_ordenacao_e_a_mais_recente_primeiro(self, cliente, muitas_analises):
        datas = [x['data'] for x in cliente.get('/analisesolo/', {'page_size': 12}).data['results']]
        assert datas == sorted(datas, reverse=True)


# ==========================================================================
# Filtros
# ==========================================================================

class TestFiltros:
    def test_por_gleba(self, cliente, cadastros, muitas_analises):
        from core.models import Gleba
        outra = Gleba.objects.create(propriedade=cadastros['propriedade'],
                                     nome='Talhao 2')
        from conftest import criar_analise
        criar_analise(cadastros, laudo='OUTRA-GLEBA')
        # Move uma analise para a outra gleba
        alvo = muitas_analises[0]
        alvo.gleba = outra
        alvo.save()

        resposta = cliente.get('/analisesolo/', {'gleba': outra.pk})
        assert [x['id'] for x in resposta.data['results']] == [alvo.pk]

    def test_por_propriedade_atravessa_a_gleba(self, cliente, cadastros, muitas_analises):
        # A analise nao guarda propriedade: o filtro precisa chegar la pela gleba.
        resposta = cliente.get('/analisesolo/',
                               {'propriedade': cadastros['propriedade'].pk})
        assert resposta.data['count'] == 12

    def test_por_cultura(self, cliente, cadastros, muitas_analises):
        resposta = cliente.get('/analisesolo/', {'cultura': cadastros['cultura'].pk})
        assert 0 < resposta.data['count'] < 12

    def test_intervalo_de_datas(self, cliente, muitas_analises):
        resposta = cliente.get('/analisesolo/',
                               {'data_apos': '2024-06-01', 'data_antes': '2024-08-31'})
        for linha in resposta.data['results']:
            assert '2024-06-01' <= linha['data'] <= '2024-08-31'

    def test_filtros_combinam(self, cliente, cadastros, muitas_analises):
        so_cultura = cliente.get('/analisesolo/',
                                 {'cultura': cadastros['cultura'].pk}).data['count']
        combinado = cliente.get('/analisesolo/', {
            'cultura': cadastros['cultura'].pk, 'data_apos': '2024-07-01',
        }).data['count']
        assert combinado <= so_cultura

    def test_filtro_nao_atravessa_contas(self, cliente, cadastros_intruso):
        # Filtrar pela propriedade de outro nao pode devolver os dados dele.
        from conftest import criar_analise
        criar_analise(cadastros_intruso)

        resposta = cliente.get('/analisesolo/',
                               {'propriedade': cadastros_intruso['propriedade'].pk})
        assert resposta.data['count'] == 0

    def test_filtro_sem_resultado_devolve_lista_vazia_e_nao_erro(
            self, cliente, muitas_analises):
        resposta = cliente.get('/analisesolo/', {'data_apos': '2099-01-01'})
        assert resposta.status_code == status.HTTP_200_OK
        assert resposta.data['count'] == 0
