"""
Indices agronomicos derivados de uma analise de solo.

Este modulo e proposital e integralmente PURO: recebe numeros, devolve numeros,
nao importa Django nem conhece os models. Duas razoes.

A primeira e rastreabilidade. Cada numero precisa ser reproduzivel a partir da
formula, sem depender de estado de banco ou de requisicao - o que permite
conferir um resultado contra a fonte bibliografica a qualquer momento.

A segunda e teste. Funcao pura com entrada e saida conhecidas se verifica com
valores de referencia, sem subir banco.

ESCOPO
    Este e um sistema de estudo, nao um substituto do agronomo. Ele aplica os
    metodos de calculo publicados; a interpretacao e a decisao continuam sendo
    de quem entende do assunto.

UNIDADES ESPERADAS (padrao dos laboratorios brasileiros):
    Ca, Mg, K, Na, Al, H  -> cmolc/dm3
    P, S, micronutrientes -> mg/dm3
    areia, silte, argila  -> % (soma 100) ou g/kg (soma 1000)

Atencao: as bases so podem ser somadas entre si porque estao todas em
cmolc/dm3. Laboratorio que reporte potassio em mg/dm3 exige conversao
(dividir por 391) ANTES de chamar estas funcoes.
"""
from decimal import Decimal


def _d(valor):
    """Converte para Decimal, tratando ausencia como zero."""
    if valor is None:
        return Decimal('0')
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


def soma_de_bases(ca, mg, k, na):
    """SB = Ca + Mg + K + Na, em cmolc/dm3."""
    return _d(ca) + _d(mg) + _d(k) + _d(na)


def ctc_efetiva(ca, mg, k, na, al):
    """
    CTC efetiva (t) = SB + Al.

    E a capacidade de troca no pH atual do solo - a que a planta encontra hoje.
    """
    return soma_de_bases(ca, mg, k, na) + _d(al)


def ctc_potencial(ca, mg, k, na, h, al):
    """
    CTC a pH 7,0 (T) = SB + (H + Al).

    E a capacidade de troca potencial, usada como base do calculo de calagem.
    """
    return soma_de_bases(ca, mg, k, na) + _d(h) + _d(al)


def saturacao_por_bases(ca, mg, k, na, h, al):
    """
    V% = SB / T x 100.

    O indicador central do diagnostico: quanto da capacidade de troca esta
    ocupada por bases (as boas) em vez de acidez.
    """
    t = ctc_potencial(ca, mg, k, na, h, al)
    if t == 0:
        return None
    return soma_de_bases(ca, mg, k, na) / t * 100


def saturacao_por_aluminio(ca, mg, k, na, al):
    """
    m% = Al / t x 100.

    Mede a toxidez por aluminio. Acima de certos limites a raiz nao se
    desenvolve, independentemente da fertilidade do resto.
    """
    t_efetiva = ctc_efetiva(ca, mg, k, na, al)
    if t_efetiva == 0:
        return None
    return _d(al) / t_efetiva * 100


def relacao(numerador, denominador):
    """Razao entre duas bases. None quando o denominador e zero."""
    d = _d(denominador)
    if d == 0:
        return None
    return _d(numerador) / d


# Percentual de cada base sobre a CTC potencial. Ajuda a ver desequilibrio
# mesmo quando o V% total esta adequado.
def participacao_na_ctc(valor, ca, mg, k, na, h, al):
    t = ctc_potencial(ca, mg, k, na, h, al)
    if t == 0:
        return None
    return _d(valor) / t * 100


# --------------------------------------------------------------------------
# Granulometria
# --------------------------------------------------------------------------

def normalizar_granulometria(areia, silte, argila):
    """
    Devolve as tres fracoes em porcentagem, aceitando entrada em % ou g/kg.

    O formulario sugere porcentagem, mas o campo comporta g/kg e laudos usam
    as duas convencoes. Decide pela soma, nao por configuracao, para nao
    depender de alguem marcar a unidade certa.
    """
    a, s, ar = _d(areia), _d(silte), _d(argila)
    soma = a + s + ar
    if soma == 0:
        return None
    # Perto de 1000 => g/kg; perto de 100 => ja esta em porcentagem.
    if abs(soma - 1000) <= 20:
        return (a / 10, s / 10, ar / 10)
    return (a, s, ar)


def classe_textural(areia, silte, argila):
    """
    Classe textural simplificada, pelos grupos usados em recomendacao de
    adubacao no Brasil (agrupamento por teor de argila).

    Nao e o triangulo textural completo da Sociedade Brasileira de Ciencia do
    Solo, que distingue 13 classes. E o agrupamento em 4 grupos que as tabelas
    de recomendacao efetivamente usam para escolher a dose de fosforo.
    """
    normalizada = normalizar_granulometria(areia, silte, argila)
    if normalizada is None:
        return None
    _, _, argila_pct = normalizada

    if argila_pct <= 15:
        return 'Arenosa'
    if argila_pct <= 35:
        return 'Textura média'
    if argila_pct <= 60:
        return 'Argilosa'
    return 'Muito argilosa'


# --------------------------------------------------------------------------
# Diagnostico consolidado
# --------------------------------------------------------------------------

def _arredonda(valor, casas=2):
    if valor is None:
        return None
    return valor.quantize(Decimal('1.' + '0' * casas))


def diagnostico(analise):
    """
    Calcula todos os indices de uma analise.

    Recebe qualquer objeto com os atributos da analise (a instancia do model
    serve, mas um objeto simples tambem) e devolve um dicionario. Nao grava
    nada: os indices sao derivados e devem ser recalculados a partir da fonte,
    para nunca ficarem defasados em relacao aos valores que os originaram.
    """
    ca, mg, k, na = analise.ca, analise.mg, analise.k, analise.na
    h, al = analise.h, analise.al

    sb = soma_de_bases(ca, mg, k, na)
    t_ef = ctc_efetiva(ca, mg, k, na, al)
    t_pot = ctc_potencial(ca, mg, k, na, h, al)

    return {
        'soma_bases': _arredonda(sb),
        'ctc_efetiva': _arredonda(t_ef),
        'ctc_potencial': _arredonda(t_pot),
        'saturacao_bases': _arredonda(saturacao_por_bases(ca, mg, k, na, h, al), 1),
        'saturacao_aluminio': _arredonda(saturacao_por_aluminio(ca, mg, k, na, al), 1),
        'relacao_ca_mg': _arredonda(relacao(ca, mg)),
        'relacao_ca_k': _arredonda(relacao(ca, k)),
        'relacao_mg_k': _arredonda(relacao(mg, k)),
        'participacao_ca': _arredonda(participacao_na_ctc(ca, ca, mg, k, na, h, al), 1),
        'participacao_mg': _arredonda(participacao_na_ctc(mg, ca, mg, k, na, h, al), 1),
        'participacao_k': _arredonda(participacao_na_ctc(k, ca, mg, k, na, h, al), 1),
        'classe_textural': classe_textural(analise.areia, analise.silte, analise.argila),
    }


# ==========================================================================
# CALAGEM
#
# Metodo da saturacao por bases, o mais difundido no Brasil. A referencia
# classica e o Boletim Tecnico 100 do IAC; a 5a Aproximacao (CFSEMG) e os
# boletins da Embrapa Cerrados usam a mesma equacao, variando os parametros
# (V2 por cultura, coeficientes do metodo do aluminio).
#
# O que este modulo NAO faz: doses de N, P e K. Elas nao saem de formula -
# vem de tabelas de calibracao empirica, por regiao e cultura. Inventa-las
# produziria numeros com aparencia de autoridade e sem lastro.
# ==========================================================================

# Camada de referencia da calagem, em cm. As formulas abaixo dao a dose para
# incorporar nesta profundidade.
CAMADA_CALAGEM_CM = 20


def necessidade_calagem_por_saturacao(ca, mg, k, na, h, al, v2):
    """
    NC = T x (V2 - V1) / 100, em t/ha de corretivo com PRNT 100%.

    V1 e a saturacao atual (calculada da analise) e V2 e a desejada para a
    cultura. Devolve None se faltar V2, e zero quando o solo ja esta no alvo -
    nesse caso calcario nao corrige nada, so gasta.
    """
    if v2 is None:
        return None

    v1 = saturacao_por_bases(ca, mg, k, na, h, al)
    if v1 is None:
        return None

    t = ctc_potencial(ca, mg, k, na, h, al)
    nc = t * (_d(v2) - v1) / 100
    return nc if nc > 0 else Decimal('0')


def necessidade_calagem_por_aluminio(ca, mg, al, fator_al=2, minimo_ca_mg=2):
    """
    NC = fator x Al + [minimo - (Ca + Mg)], em t/ha.

    Alternativa usada onde a toxidez por aluminio manda mais que a saturacao,
    tipicamente em solos de Cerrado. Vantagem pratica: nao depende de nenhum
    parametro por cultura, entao funciona mesmo sem V2 cadastrado.

    Os coeficientes variam conforme a fonte e a textura do solo; os padroes
    aqui (2 e 2) sao os mais citados.
    """
    corrigir_al = _d(fator_al) * _d(al)
    repor_bases = _d(minimo_ca_mg) - (_d(ca) + _d(mg))
    nc = corrigir_al + max(repor_bases, Decimal('0'))
    return nc if nc > 0 else Decimal('0')


def dose_corretivo(necessidade, prnt):
    """
    Converte a necessidade teorica (PRNT 100%) na dose real do produto:

        dose = NC x 100 / PRNT

    Um calcario de PRNT 70% exige mais produto para o mesmo efeito que um de
    PRNT 90%. E por isso que o PRNT precisa estar cadastrado.
    """
    if necessidade is None or prnt is None:
        return None
    prnt = _d(prnt)
    if prnt <= 0:
        return None
    return _d(necessidade) * 100 / prnt


def tipo_calcario_indicado(ca, mg):
    """
    Escolhe o corretivo pela relacao Ca:Mg do solo.

    Muito calcio em relacao ao magnesio pede um corretivo que reponha Mg
    (dolomitico); com Mg ja adequado, o calcitico basta. E o criterio que
    justifica os tres campos de calcario na Recomendacao.
    """
    r = relacao(ca, mg)
    if r is None:
        # Sem magnesio detectavel: o corretivo precisa fornece-lo.
        return 'dolomitico'
    if r > 4:
        return 'dolomitico'
    if r > 3:
        return 'magnesiano'
    return 'calcitico'


# Faixas de interpretacao de uso corrente. Servem para traduzir o numero em
# leitura - "V% 45" diz pouco a quem nao e da area; "baixo" diz muito.
FAIXAS_V = [
    (25, 'Muito baixo'), (50, 'Baixo'), (70, 'Médio'), (90, 'Bom'),
]
FAIXAS_M = [
    (15, 'Baixo'), (30, 'Médio'), (50, 'Alto'),
]


def _classificar(valor, faixas, acima='Muito alto'):
    if valor is None:
        return None
    for limite, rotulo in faixas:
        if valor <= limite:
            return rotulo
    return acima


def classificar_saturacao_bases(v):
    return _classificar(v, FAIXAS_V)


def classificar_saturacao_aluminio(m):
    return _classificar(m, FAIXAS_M)


def recomendacao_calagem(analise, v2=None, prnt=None):
    """
    Monta a recomendacao de calagem de uma analise.

    'v2' vem da cultura e 'prnt' do calcario escolhido; ambos opcionais. Sem
    v2, o metodo da saturacao nao roda, mas o do aluminio sim - por isso os
    dois aparecem no resultado. Sem prnt, sai a necessidade teorica e a dose
    real fica em aberto.

    Calcula apenas para a camada superficial: e para ela que a equacao foi
    calibrada.
    """
    if analise.camada != '0-20':
        return {
            'aplicavel': False,
            'motivo': (
                'A calagem é calculada sobre a camada de 0 a 20 cm. '
                f'Esta análise é da camada {analise.camada} cm.'
            ),
        }

    ca, mg, k, na = analise.ca, analise.mg, analise.k, analise.na
    h, al = analise.h, analise.al

    nc_saturacao = necessidade_calagem_por_saturacao(ca, mg, k, na, h, al, v2)
    nc_aluminio = necessidade_calagem_por_aluminio(ca, mg, al)
    # Quando ha V2 cadastrado, ele manda: e o metodo de referencia.
    nc = nc_saturacao if nc_saturacao is not None else nc_aluminio

    return {
        'aplicavel': True,
        'metodo': 'Saturação por bases' if nc_saturacao is not None else 'Alumínio e Ca+Mg',
        'v2_utilizado': _arredonda(_d(v2), 1) if v2 is not None else None,
        'necessidade_saturacao_t_ha': _arredonda(nc_saturacao),
        'necessidade_aluminio_t_ha': _arredonda(nc_aluminio),
        'necessidade_t_ha': _arredonda(nc),
        'prnt_utilizado': _arredonda(_d(prnt), 1) if prnt is not None else None,
        'dose_corretivo_t_ha': _arredonda(dose_corretivo(nc, prnt)),
        'tipo_indicado': tipo_calcario_indicado(ca, mg),
        'camada_cm': CAMADA_CALAGEM_CM,
    }
