"""
Validadores de dominio compartilhados entre as apps.

Fica na raiz de 'apps/', que o config/settings.py acrescenta ao sys.path, e por
isso e importavel como 'validadores' tanto de core quanto de autenticacao.

Os validadores sao declarados nos campos dos models. Assim valem de uma vez no
DRF (que os aplica ao montar o serializer) e no /admin, sem precisar repetir a
regra em cada lugar.
"""
import re
from datetime import date

from django.core.exceptions import ValidationError


# Unidades da federacao. Usado como 'choices' nos campos 'estado', que antes
# eram texto livre de 2 posicoes e aceitavam qualquer coisa, inclusive "XX".
UFS = [
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
    ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
    ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'),
    ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
]


def validar_cpf(valor):
    """
    Confere os dois digitos verificadores do CPF.

    Aceita com ou sem pontuacao. Antes o campo era CharField livre e engolia
    '00000000000' ou qualquer sequencia de 11 numeros.
    """
    digitos = re.sub(r'\D', '', valor or '')

    if len(digitos) != 11:
        raise ValidationError('O CPF deve conter 11 dígitos.')

    # Sequencias repetidas (111.111.111-11 etc.) passam no calculo dos digitos,
    # entao precisam ser barradas a parte.
    if digitos == digitos[0] * 11:
        raise ValidationError('CPF inválido.')

    for posicao in (9, 10):
        soma = sum(
            int(digitos[i]) * ((posicao + 1) - i) for i in range(posicao)
        )
        verificador = (soma * 10) % 11
        if verificador == 10:
            verificador = 0
        if verificador != int(digitos[posicao]):
            raise ValidationError('CPF inválido.')


def validar_telefone(valor):
    """
    Exige um telefone brasileiro plausivel: 10 digitos (fixo com DDD) ou
    11 (celular com DDD). Pontuacao e ignorada.
    """
    digitos = re.sub(r'\D', '', valor or '')

    if len(digitos) not in (10, 11):
        raise ValidationError(
            'Informe o telefone com DDD: 10 dígitos para fixo ou 11 para celular.'
        )


def validar_data_nao_futura(valor):
    """Uma analise nao pode ter sido feita depois de hoje."""
    if valor and valor > date.today():
        raise ValidationError('A data não pode estar no futuro.')


def validar_soma_granulometrica(areia, silte, argila):
    """
    Areia, silte e argila sao fracoes do mesmo volume: precisam somar o total.

    Aceita as duas convencoes usadas em laudo - porcentagem (soma 100) e
    g/kg (soma 1000) - com folga de 2% para arredondamento do laboratorio.
    Retorna a mensagem de erro, ou None se estiver coerente.

    PARA FIXAR UMA UNICA UNIDADE: deixe apenas o total desejado na lista
    'totais_aceitos' abaixo.
    """
    if areia is None or silte is None or argila is None:
        return None

    soma = float(areia) + float(silte) + float(argila)
    totais_aceitos = (100, 1000)

    for total in totais_aceitos:
        if abs(soma - total) <= total * 0.02:
            return None

    return (
        f'Areia, silte e argila somam {soma:.2f}. '
        'A soma deve ser 100 (porcentagem) ou 1000 (g/kg).'
    )
