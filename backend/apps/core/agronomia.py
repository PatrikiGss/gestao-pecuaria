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
# Sobre as doses de adubo (secao ADUBACAO, mais abaixo): elas saem de formula
# aqui, mas as formulas dependem de parametros por cultura - saturacao de K
# desejada, teor de fosforo alvo, fator de fixacao. Esses parametros vem da
# fonte de referencia adotada e sao cadastrados na Cultura. O modulo aplica;
# nao arbitra valores.
#
# Excecao declarada: o NITROGENIO nao e derivavel da analise de solo. O N
# disponivel depende da mineralizacao da materia organica, do historico da
# area e da produtividade esperada - nenhum metodo o calcula a partir de um
# teor medido no laudo. Ele entra como dose cadastrada na cultura.
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


# ==========================================================================
# ADUBACAO
#
# As conversoes abaixo saem da estequiometria, nao de tabela - por isso podem
# ser conferidas com papel e lapis:
#
#   Volume de 1 ha na camada de 0-20 cm:
#       10.000 m2 x 0,20 m = 2.000 m3 = 2.000.000 dm3
#
#   Potassio: 1 cmolc/dm3 de K = 0,01 mol x 39,098 g = 0,39098 g/dm3
#       0,39098 g/dm3 x 2.000.000 dm3 = 781.960 g = 782 kg K/ha
#       K -> K2O: 94,196 / 78,196 = 1,2046
#       Logo 1 cmolc/dm3 de K equivale a ~942 kg de K2O por hectare.
#
#   Fosforo: 1 mg/dm3 x 2.000.000 dm3 = 2.000.000 mg = 2 kg P/ha
#       P -> P2O5: 141,94 / 61,948 = 2,2914
#       Mas o solo FIXA fosforo, e quanto mais argiloso mais fixa. Por isso a
#       dose usa um fator de fixacao cadastrado por cultura, e nao a conversao
#       estequiometrica pura.
#
#   Enxofre: mesma logica de volume; 1 mg/dm3 = 2 kg S/ha.
# ==========================================================================

# Massa de solo/volume considerado: 1 ha na camada de 0-20 cm, em dm3.
VOLUME_HECTARE_20CM = Decimal('2000000')

CMOLC_K_PARA_KG_K2O = Decimal('942')   # 1 cmolc/dm3 de K -> kg de K2O/ha
MG_DM3_PARA_KG_HA = Decimal('2')       # 1 mg/dm3 -> kg/ha na camada de 20 cm
TEOR_K2O_NO_KCL = Decimal('0.60')      # cloreto de potassio comercial: 60% K2O


def necessidade_potassio(ca, mg, k, na, h, al, saturacao_k_desejada):
    """
    Dose de K2O, em kg/ha, pelo metodo da saturacao por potassio.

    O alvo e uma participacao de K na CTC (tipicamente 3% a 5%). A dose e a
    diferenca entre o K que essa participacao exige e o K que o solo ja tem.

    Devolve None sem o parametro, e zero quando o solo ja atingiu o alvo.
    """
    if saturacao_k_desejada is None:
        return None

    t = ctc_potencial(ca, mg, k, na, h, al)
    if t == 0:
        return None

    k_alvo = t * _d(saturacao_k_desejada) / 100          # cmolc/dm3
    falta = k_alvo - _d(k)
    if falta <= 0:
        return Decimal('0')
    return falta * CMOLC_K_PARA_KG_K2O


def dose_kcl(k2o_kg_ha):
    """Converte a necessidade de K2O na quantidade de cloreto de potassio."""
    if k2o_kg_ha is None:
        return None
    return _d(k2o_kg_ha) / TEOR_K2O_NO_KCL


def necessidade_fosforo(p_atual, p_desejado, fator_fixacao):
    """
    Dose de P2O5, em kg/ha, pelo metodo de elevacao do teor.

    dose = (P desejado - P atual) x fator de fixacao

    O fator representa quanto de P2O5 e preciso aplicar para elevar 1 mg/dm3
    no solo. Nao e a conversao estequiometrica (que daria 4,58): o solo fixa
    parte do fosforo, e quanto mais argiloso, mais fixa. Por isso o valor e
    cadastrado, e nao embutido aqui.
    """
    if p_desejado is None or fator_fixacao is None:
        return None
    falta = _d(p_desejado) - _d(p_atual)
    if falta <= 0:
        return Decimal('0')
    return falta * _d(fator_fixacao)


def necessidade_enxofre(s_atual, s_desejado):
    """Dose de S, em kg/ha, para elevar o teor ate o alvo."""
    if s_desejado is None:
        return None
    falta = _d(s_desejado) - _d(s_atual)
    if falta <= 0:
        return Decimal('0')
    return falta * MG_DM3_PARA_KG_HA


def necessidade_gesso(argila_pct, saturacao_al, ca):
    """
    Dose de gesso agricola, em kg/ha.

    Criterio de uso corrente: indica-se gessagem quando ha toxidez por
    aluminio (m% acima de 20) ou calcio escasso (abaixo de 0,5 cmolc/dm3).
    A dose usa o teor de argila, porque a retencao de sulfato acompanha a
    fracao argilosa:  dose = 50 x argila(%)

    Devolve zero quando nao ha indicacao - e uma resposta, nao uma omissao.
    """
    if argila_pct is None:
        return None

    indicado = (saturacao_al is not None and saturacao_al > 20) or _d(ca) < Decimal('0.5')
    if not indicado:
        return Decimal('0')
    return Decimal('50') * _d(argila_pct)


def recomendacao_completa(analise, cultura=None, calcario=None):
    """
    Monta a recomendacao inteira de uma analise: todos os campos calculados.

    'cultura' fornece os parametros (V2, saturacao de K, fosforo alvo, fator de
    fixacao, N e S). 'calcario' fornece o PRNT. Faltando qualquer um, o campo
    correspondente sai vazio e a chave 'pendencias' diz o que preencher - em
    vez de devolver um numero sem lastro.

    A calagem sai num unico campo, o do tipo indicado pela relacao Ca:Mg. Os
    outros dois ficam zerados: recomendar tres corretivos ao mesmo tempo para
    a mesma area nao faria sentido agronomico.
    """
    cultura = cultura or getattr(analise, 'cultura', None)
    ca, mg, k, na = analise.ca, analise.mg, analise.k, analise.na
    h, al = analise.h, analise.al

    pendencias = []

    def parametro(nome, mensagem):
        valor = getattr(cultura, nome, None) if cultura else None
        if valor is None:
            pendencias.append(mensagem)
        return valor

    nome_cultura = getattr(cultura, 'nome', 'a cultura') if cultura else 'a cultura'

    # ------------------------------------------------------------ calagem
    v2 = parametro('saturacao_bases_desejada',
                   f'{nome_cultura}: falta a saturação por bases desejada (V₂).')
    nc = necessidade_calagem_por_saturacao(ca, mg, k, na, h, al, v2)
    metodo = 'Saturação por bases'
    if nc is None:
        # Sem V2 o metodo do aluminio ainda funciona: nao depende da cultura.
        nc = necessidade_calagem_por_aluminio(ca, mg, al)
        metodo = 'Alumínio e Ca+Mg'

    prnt = getattr(calcario, 'prnt', None) if calcario else None
    if prnt is None:
        pendencias.append('Nenhum calcário cadastrado do tipo indicado.')
    dose = dose_corretivo(nc, prnt)

    tipo = tipo_calcario_indicado(ca, mg)
    calcarios = {'calcitico': Decimal('0'), 'magnesiano': Decimal('0'), 'dolomitico': Decimal('0')}
    calcarios[tipo] = _arredonda(dose) if dose is not None else Decimal('0')

    # ----------------------------------------------------------- gessagem
    normalizada = normalizar_granulometria(analise.areia, analise.silte, analise.argila)
    argila_pct = normalizada[2] if normalizada else None
    m = saturacao_por_aluminio(ca, mg, k, na, al)
    gesso = necessidade_gesso(argila_pct, m, ca)

    # --------------------------------------------------------------- NPK+S
    sat_k = parametro('saturacao_k_desejada',
                      f'{nome_cultura}: falta a saturação de K desejada.')
    k2o = necessidade_potassio(ca, mg, k, na, h, al, sat_k)
    kcl = dose_kcl(k2o)

    p_alvo = parametro('fosforo_desejado', f'{nome_cultura}: falta o fósforo desejado.')
    fator = parametro('fator_fixacao_fosforo',
                      f'{nome_cultura}: falta o fator de fixação de fósforo.')
    p2o5 = necessidade_fosforo(analise.p, p_alvo, fator)

    n = parametro('nitrogenio_recomendado',
                  f'{nome_cultura}: falta a dose de nitrogênio. '
                  'O N não é calculável a partir da análise de solo.')

    s_alvo = parametro('enxofre_desejado', f'{nome_cultura}: falta o enxofre desejado.')
    enxofre = necessidade_enxofre(analise.s, s_alvo)

    return {
        'camada_correcao': f'0-{CAMADA_CALAGEM_CM} cm',
        'calcario_calcitico': calcarios['calcitico'],
        'calcario_dolomitico': calcarios['dolomitico'],
        'calcario_magnesiano': calcarios['magnesiano'],
        'gesso': _arredonda(gesso),
        'kcl': _arredonda(kcl),
        'p2o5': _arredonda(p2o5),
        'n': _arredonda(_d(n)) if n is not None else None,
        's': _arredonda(enxofre),
        # Contexto do calculo, para a tela explicar de onde veio cada numero.
        'metodo_calagem': metodo,
        'tipo_calcario': tipo,
        'necessidade_calagem_t_ha': _arredonda(nc),
        'v2_utilizado': _arredonda(_d(v2), 1) if v2 is not None else None,
        'prnt_utilizado': _arredonda(_d(prnt), 1) if prnt is not None else None,
        'k2o_kg_ha': _arredonda(k2o),
        'pendencias': pendencias,
    }
