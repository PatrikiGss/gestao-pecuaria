"""
Testes do agronomia.py.

POR QUE ESTE ARQUIVO VEM PRIMEIRO

O modulo e puro - recebe numeros, devolve numeros, nao importa Django - entao
se verifica sem subir banco. E carrega a parte do sistema que mais precisa de
rede de protecao: e dele que saem as doses que alguem vai aplicar num hectare.

OS NUMEROS ESPERADOS SAO CALCULADOS A MAO, e a conta fica escrita ao lado de
cada um. Um teste que compare a funcao com ela mesma - rodando o codigo para
descobrir o resultado e fixando esse resultado - nao verifica nada: passaria
igual se a formula estivesse errada desde o inicio. O valor so tem lastro se
vier de fora do codigo.

Os perfis usados sao os mesmos do comando dados_exemplo, de proposito: assim o
que os testes afirmam e o que se ve na tela ao conferir o sistema a mao.
"""
from decimal import Decimal

import pytest

from core import agronomia

# Perfis de solo do dados_exemplo. Bases em cmolc/dm3.
MUITO_ACIDO = dict(ca='0.80', mg='0.30', k='0.08', na='0.02', al='1.20', h='5.50')
ACIDO = dict(ca='1.80', mg='0.70', k='0.12', na='0.03', al='0.60', h='4.20')
MEDIO = dict(ca='3.00', mg='1.50', k='0.20', na='0.05', al='0.20', h='3.05')
BOM = dict(ca='4.50', mg='2.00', k='0.35', na='0.05', al='0.00', h='1.80')


def bases(perfil):
    return perfil['ca'], perfil['mg'], perfil['k'], perfil['na']


# ==========================================================================
# Indices basicos
# ==========================================================================

class TestSomaDeBases:
    def test_soma_as_quatro_bases(self):
        # 0,80 + 0,30 + 0,08 + 0,02 = 1,20
        assert agronomia.soma_de_bases('0.80', '0.30', '0.08', '0.02') == Decimal('1.20')

    def test_trata_ausencia_como_zero(self):
        # Sodio costuma nao vir no laudo. Faltando, entra como zero em vez de
        # explodir - a analise continua interpretavel sem ele.
        assert agronomia.soma_de_bases('2.00', '1.00', '0.10', None) == Decimal('3.10')

    def test_aceita_decimal_e_string(self):
        # Os valores chegam como Decimal vindos do banco e como string vindos
        # do formulario; os dois caminhos precisam dar o mesmo numero.
        a = agronomia.soma_de_bases(Decimal('1.5'), Decimal('0.5'), 0, 0)
        b = agronomia.soma_de_bases('1.5', '0.5', '0', '0')
        assert a == b == Decimal('2.0')


class TestCTC:
    def test_ctc_efetiva_soma_aluminio(self):
        # t = SB + Al = 1,20 + 1,20 = 2,40
        assert agronomia.ctc_efetiva(*bases(MUITO_ACIDO), MUITO_ACIDO['al']) == Decimal('2.40')

    def test_ctc_potencial_soma_hidrogenio_e_aluminio(self):
        # T = SB + H + Al = 1,20 + 5,50 + 1,20 = 7,90
        t = agronomia.ctc_potencial(*bases(MUITO_ACIDO), MUITO_ACIDO['h'], MUITO_ACIDO['al'])
        assert t == Decimal('7.90')

    def test_potencial_e_maior_que_efetiva_em_solo_acido(self):
        # A diferenca entre as duas e o H, que so troca acima do pH atual.
        efetiva = agronomia.ctc_efetiva(*bases(ACIDO), ACIDO['al'])
        potencial = agronomia.ctc_potencial(*bases(ACIDO), ACIDO['h'], ACIDO['al'])
        assert potencial > efetiva


class TestSaturacaoPorBases:
    @pytest.mark.parametrize('perfil, esperado', [
        # V% = SB / T x 100
        (MUITO_ACIDO, Decimal('15.2')),   # 1,20 / 7,90 = 0,151898... -> 15,2
        (ACIDO, Decimal('35.6')),         # 2,65 / 7,45 = 0,355704... -> 35,6
        (MEDIO, Decimal('59.4')),         # 4,75 / 8,00 = 0,59375    -> 59,4
        (BOM, Decimal('79.3')),           # 6,90 / 8,70 = 0,793103... -> 79,3
    ])
    def test_serie_historica_do_dados_exemplo(self, perfil, esperado):
        """
        A serie de 15,2 a 79,3 e a mesma que o dados_exemplo cria numa gleba
        para mostrar o solo respondendo ao manejo ao longo de quatro anos.
        """
        v = agronomia.saturacao_por_bases(*bases(perfil), perfil['h'], perfil['al'])
        assert agronomia._arredonda(v, 1) == esperado

    def test_devolve_none_quando_a_ctc_e_zero(self):
        # Divisao por zero nao pode virar excecao nem zero: o correto e "nao da
        # para saber", e quem exibe mostra um travessao.
        assert agronomia.saturacao_por_bases(0, 0, 0, 0, 0, 0) is None


class TestSaturacaoPorAluminio:
    def test_solo_muito_acido(self):
        # m% = Al / t x 100 = 1,20 / 2,40 = 50,0
        m = agronomia.saturacao_por_aluminio(*bases(MUITO_ACIDO), MUITO_ACIDO['al'])
        assert agronomia._arredonda(m, 1) == Decimal('50.0')

    def test_solo_sem_aluminio_da_zero(self):
        m = agronomia.saturacao_por_aluminio(*bases(BOM), BOM['al'])
        assert agronomia._arredonda(m, 1) == Decimal('0.0')


class TestRelacoes:
    def test_calcio_magnesio(self):
        assert agronomia.relacao('4.50', '2.00') == Decimal('2.25')

    def test_denominador_zero_devolve_none(self):
        # Sem magnesio detectavel a relacao nao existe. Devolver zero seria
        # pior: zero se leria como "equilibrado".
        assert agronomia.relacao('4.50', '0') is None


# ==========================================================================
# Granulometria
# ==========================================================================

class TestGranulometria:
    def test_aceita_porcentagem(self):
        assert agronomia.normalizar_granulometria('25', '25', '50') == (
            Decimal('25'), Decimal('25'), Decimal('50'))

    def test_converte_g_por_kg(self):
        # Laudo em g/kg soma 1000. A funcao decide pela soma, e nao por
        # configuracao, para nao depender de alguem marcar a unidade certa.
        a, s, ar = agronomia.normalizar_granulometria('250', '250', '500')
        assert (a, s, ar) == (Decimal('25'), Decimal('25'), Decimal('50'))

    def test_soma_zero_devolve_none(self):
        assert agronomia.normalizar_granulometria(0, 0, 0) is None

    @pytest.mark.parametrize('argila, classe', [
        ('10', 'Arenosa'),
        ('15', 'Arenosa'),          # limite superior fecha em Arenosa
        ('16', 'Textura média'),
        ('35', 'Textura média'),
        ('36', 'Argilosa'),
        ('60', 'Argilosa'),
        ('61', 'Muito argilosa'),
    ])
    def test_classe_textural_nos_limites(self, argila, classe):
        # Os limites sao onde erro de comparacao aparece (<= vs <), entao os
        # casos testados sao os das bordas, e nao valores confortaveis.
        resto = (Decimal('100') - Decimal(argila)) / 2
        assert agronomia.classe_textural(resto, resto, argila) == classe


# ==========================================================================
# Calagem
# ==========================================================================

class TestCalagem:
    def test_necessidade_por_saturacao(self):
        # NC = T x (V2 - V1) / 100
        # T = 7,90 ; V1 = 15,1898... ; V2 = 70
        # NC = 7,90 x 54,8101... / 100 = 4,33 t/ha
        nc = agronomia.necessidade_calagem_por_saturacao(
            *bases(MUITO_ACIDO), MUITO_ACIDO['h'], MUITO_ACIDO['al'], v2='70')
        assert agronomia._arredonda(nc) == Decimal('4.33')

    def test_sem_v2_nao_calcula(self):
        # Cultura sem parametro cadastrado nao pode receber dose arbitraria.
        nc = agronomia.necessidade_calagem_por_saturacao(
            *bases(MUITO_ACIDO), MUITO_ACIDO['h'], MUITO_ACIDO['al'], v2=None)
        assert nc is None

    def test_solo_ja_no_alvo_nao_recebe_calcario(self):
        # V1 = 79,3 e V2 = 70: o solo ja passou do alvo. Zero, e nao negativo -
        # calcario a mais nao "descorrige" nada, so gasta.
        nc = agronomia.necessidade_calagem_por_saturacao(
            *bases(BOM), BOM['h'], BOM['al'], v2='70')
        assert nc == Decimal('0')

    def test_metodo_do_aluminio(self):
        # NC = 2 x Al + [2 - (Ca + Mg)]
        #    = 2 x 1,20 + [2 - 1,10] = 2,40 + 0,90 = 3,30
        nc = agronomia.necessidade_calagem_por_aluminio(
            MUITO_ACIDO['ca'], MUITO_ACIDO['mg'], MUITO_ACIDO['al'])
        assert nc == Decimal('3.30')

    def test_metodo_do_aluminio_nao_desconta_bases_em_excesso(self):
        # Com Ca+Mg = 6,50 acima do minimo de 2, a parcela de reposicao e zero
        # e nao negativa: sobra de bases nao reduz a necessidade de neutralizar
        # o aluminio.
        nc = agronomia.necessidade_calagem_por_aluminio('4.50', '2.00', '0.50')
        assert nc == Decimal('1.00')   # 2 x 0,50 + 0

    def test_dose_corrige_pelo_prnt(self):
        # dose = NC x 100 / PRNT = 4,00 x 100 / 80 = 5,00
        assert agronomia.dose_corretivo('4.00', '80') == Decimal('5')

    def test_prnt_maior_exige_menos_produto(self):
        muito = agronomia.dose_corretivo('4.00', '70')
        pouco = agronomia.dose_corretivo('4.00', '95')
        assert muito > pouco

    @pytest.mark.parametrize('prnt', [None, 0, '0', '-10'])
    def test_prnt_invalido_nao_produz_dose(self, prnt):
        assert agronomia.dose_corretivo('4.00', prnt) is None

    @pytest.mark.parametrize('ca, mg, tipo', [
        ('4.50', '0.45', 'dolomitico'),    # 10:1, muito acima de 4
        ('4.50', '1.00', 'dolomitico'),    # 4,5:1
        # As faixas sao abertas embaixo e fechadas em cima: "acima de 4" e
        # estritamente maior, entao 4:1 exato ainda e magnesiano. Os dois casos
        # abaixo fixam justamente essas bordas, que sao onde uma troca de > por
        # >= passaria despercebida.
        ('4.00', '1.00', 'magnesiano'),    # 4:1 - nao e "> 4"
        ('3.50', '1.00', 'magnesiano'),    # 3,5:1
        ('3.00', '1.00', 'calcitico'),     # 3:1 - nao e "> 3"
        ('2.00', '1.00', 'calcitico'),
        ('4.50', '0', 'dolomitico'),       # sem magnesio: o corretivo repoe
    ])
    def test_tipo_pela_relacao_calcio_magnesio(self, ca, mg, tipo):
        assert agronomia.tipo_calcario_indicado(ca, mg) == tipo


class TestFaixasDeInterpretacao:
    @pytest.mark.parametrize('v, faixa', [
        (Decimal('15.2'), 'Muito baixo'),
        (Decimal('25'), 'Muito baixo'),
        (Decimal('35.6'), 'Baixo'),
        (Decimal('59.4'), 'Médio'),
        (Decimal('79.3'), 'Bom'),
        (Decimal('95'), 'Muito alto'),
    ])
    def test_classificacao_da_saturacao_por_bases(self, v, faixa):
        assert agronomia.classificar_saturacao_bases(v) == faixa

    def test_none_continua_none(self):
        assert agronomia.classificar_saturacao_bases(None) is None


# ==========================================================================
# Adubacao
# ==========================================================================

class TestPotassio:
    def test_dose_pela_saturacao_desejada(self):
        # T = 7,90 ; alvo de 4% => K alvo = 0,316 cmolc/dm3
        # falta = 0,316 - 0,08 = 0,236
        # 0,236 x 942 = 222,312 kg de K2O/ha
        k2o = agronomia.necessidade_potassio(
            *bases(MUITO_ACIDO), MUITO_ACIDO['h'], MUITO_ACIDO['al'],
            saturacao_k_desejada='4')
        assert agronomia._arredonda(k2o) == Decimal('222.31')

    def test_solo_no_alvo_nao_recebe_potassio(self):
        # K = 0,35 num T de 8,70 ja da 4,02%, acima do alvo de 4%.
        k2o = agronomia.necessidade_potassio(
            *bases(BOM), BOM['h'], BOM['al'], saturacao_k_desejada='4')
        assert k2o == Decimal('0')

    def test_sem_parametro_nao_calcula(self):
        assert agronomia.necessidade_potassio(
            *bases(BOM), BOM['h'], BOM['al'], saturacao_k_desejada=None) is None

    def test_conversao_para_cloreto_de_potassio(self):
        # O KCl comercial tem 60% de K2O: 600 / 0,60 = 1000 kg de produto.
        assert agronomia.dose_kcl('600') == Decimal('1000')


class TestFosforo:
    def test_dose_pelo_fator_de_fixacao(self):
        # (18 - 4) x 5 = 70 kg de P2O5/ha
        assert agronomia.necessidade_fosforo('4', '18', '5') == Decimal('70')

    def test_teor_acima_do_alvo_dispensa_adubacao(self):
        assert agronomia.necessidade_fosforo('25', '18', '5') == Decimal('0')

    @pytest.mark.parametrize('alvo, fator', [(None, '5'), ('18', None), (None, None)])
    def test_falta_de_parametro_impede_o_calculo(self, alvo, fator):
        assert agronomia.necessidade_fosforo('4', alvo, fator) is None


class TestEnxofre:
    def test_dose_pela_diferenca_de_teor(self):
        # (10 - 6) x 2 kg/ha por mg/dm3 = 8
        assert agronomia.necessidade_enxofre('6', '10') == Decimal('8')

    def test_sem_alvo_nao_calcula(self):
        assert agronomia.necessidade_enxofre('6', None) is None


class TestGesso:
    def test_indicado_por_toxidez_de_aluminio(self):
        # m% = 50, acima de 20 => 50 x argila(50%) = 2500 kg/ha
        assert agronomia.necessidade_gesso('50', Decimal('50'), '0.80') == Decimal('2500')

    def test_indicado_por_calcio_escasso(self):
        # Ca abaixo de 0,5 indica gessagem mesmo sem aluminio alto.
        assert agronomia.necessidade_gesso('40', Decimal('5'), '0.30') == Decimal('2000')

    def test_sem_indicacao_devolve_zero_e_nao_none(self):
        # Zero e uma resposta ("nao precisa"); None seria uma omissao ("nao
        # sei"). A tela distingue as duas.
        assert agronomia.necessidade_gesso('40', Decimal('5'), '3.00') == Decimal('0')

    def test_sem_granulometria_nao_da_para_calcular(self):
        assert agronomia.necessidade_gesso(None, Decimal('50'), '0.80') is None


# ==========================================================================
# Conversoes: conferiveis pela estequiometria
# ==========================================================================

class TestConstantesDeConversao:
    def test_um_hectare_de_camada_de_20cm(self):
        # 10.000 m2 x 0,20 m = 2.000 m3 = 2.000.000 dm3
        assert agronomia.VOLUME_HECTARE_20CM == Decimal('2000000')

    def test_cmolc_de_potassio_para_kg_de_k2o(self):
        # 1 cmolc/dm3 = 0,01 mol x 39,098 g = 0,39098 g/dm3
        # x 2.000.000 dm3 = 781.960 g = 782 kg de K/ha
        # K -> K2O: 94,196 / 78,196 = 1,2046  =>  782 x 1,2046 = 942 kg
        esperado = (Decimal('0.39098') * agronomia.VOLUME_HECTARE_20CM / 1000
                    * Decimal('1.2046'))
        assert abs(agronomia.CMOLC_K_PARA_KG_K2O - esperado) < Decimal('1')

    def test_mg_por_dm3_para_kg_por_hectare(self):
        # 1 mg/dm3 x 2.000.000 dm3 = 2.000.000 mg = 2 kg/ha
        assert agronomia.MG_DM3_PARA_KG_HA == Decimal('2')
