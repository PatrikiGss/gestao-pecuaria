"""
Fixtures compartilhadas pela suite.

DOIS USUARIOS, SEMPRE

Quase todo teste aqui recebe 'usuario' e 'intruso'. Isolamento entre contas e
a garantia central deste sistema - cada conta enxerga apenas os proprios dados -
e ela so se verifica com duas contas em jogo. Um teste com um usuario so passa
mesmo quando o filtro por dono nao existe.
"""
import pytest
from rest_framework.test import APIClient

from autenticacao.models import Usuario
from core.models import (
    AnaliseSolo, Calcario, Cultura, Gleba, Laboratorio, Produtor, Propriedade,
)

# CPFs com digitos verificadores validos. O validador os confere, entao
# sequencias inventadas fariam os testes falharem por motivo errado.
CPF_DONO = '52998224725'
CPF_INTRUSO = '15350946056'

SENHA = 'Solo!Forte#2024'


def criar_usuario(email, cpf):
    return Usuario.objects.create_user(
        email=email, password=SENHA, nome=f'Conta {email}',
        cpf=cpf, telefone='4899990000',
    )


@pytest.fixture
def usuario(db):
    return criar_usuario('dono@exemplo.com', CPF_DONO)


@pytest.fixture
def intruso(db):
    """Segunda conta, usada para provar que uma nao alcanca a outra."""
    return criar_usuario('intruso@exemplo.com', CPF_INTRUSO)


@pytest.fixture
def cliente(usuario):
    api = APIClient()
    api.force_authenticate(user=usuario)
    return api


@pytest.fixture
def cliente_intruso(intruso):
    api = APIClient()
    api.force_authenticate(user=intruso)
    return api


@pytest.fixture
def anonimo():
    return APIClient()


# ---------------------------------------------------------------- dominio


def montar_cadastros(usuario, sufixo=''):
    """
    Cria a hierarquia minima para uma analise existir:
    produtor -> propriedade -> gleba, mais laboratorio e cultura.

    Devolve um dicionario para os testes pegarem so o que precisam.
    """
    produtor = Produtor.objects.create(
        usuario=usuario, cpf=CPF_DONO if not sufixo else CPF_INTRUSO,
        nome=f'Produtor{sufixo}', telefone='4899990000',
        email=f'produtor{sufixo}@exemplo.com',
    )
    propriedade = Propriedade.objects.create(
        produtor=produtor, nome=f'Fazenda{sufixo}', longitude='-50.300000',
        latitude='-27.800000', endereco='Estrada', cidade='Lages', estado='SC',
    )
    gleba = Gleba.objects.create(propriedade=propriedade, nome=f'Talhao{sufixo or " 1"}')
    laboratorio = Laboratorio.objects.create(
        usuario=usuario, nome=f'Laboratorio{sufixo}', endereco='Rua',
        cidade='Lages', estado='SC', telefone='4933330000',
        email=f'lab{sufixo}@exemplo.com',
    )
    cultura = Cultura.objects.create(usuario=usuario, nome=f'Soja{sufixo}')
    return {
        'produtor': produtor, 'propriedade': propriedade, 'gleba': gleba,
        'laboratorio': laboratorio, 'cultura': cultura,
    }


@pytest.fixture
def cadastros(usuario):
    return montar_cadastros(usuario)


@pytest.fixture
def cadastros_intruso(intruso):
    return montar_cadastros(intruso, sufixo=' do intruso')


# Perfil 'muito acido' do dados_exemplo. Os indices que ele produz estao
# calculados a mao em test_agronomia.py, entao os numeros daqui tem lastro.
PERFIL_MUITO_ACIDO = dict(
    ph_h2o='4.5', ca='0.80', mg='0.30', k='0.08', na='0.02',
    al='1.20', h='5.50', p='4', s='6', materia_organica='18',
    areia='25', silte='25', argila='50',
    mn='1.80', fe='45.00', cu='1.20', zn='2.40', b='0.35',
)


def criar_analise(cadastros, **sobrescreve):
    """
    Cria uma analise com o perfil 'muito acido' por padrao.

    Qualquer campo pode ser sobrescrito, inclusive as chaves estrangeiras -
    e o que permite montar cenarios com culturas ou glebas diferentes sem
    duplicar o dicionario de valores em cada teste.
    """
    valores = dict(
        PERFIL_MUITO_ACIDO,
        laboratorio=cadastros['laboratorio'],
        gleba=cadastros['gleba'],
        cultura=cadastros['cultura'],
        data='2024-05-10',
        camada='0-20',
        area='78.50',
        laudo='LAUDO-001',
    )
    valores.update(sobrescreve)
    return AnaliseSolo.objects.create(**valores)


@pytest.fixture
def analise(cadastros):
    return criar_analise(cadastros)


@pytest.fixture
def calcario(usuario):
    return Calcario.objects.create(
        usuario=usuario, nome='Calcitico Fornecedor A', tipo=Calcario.CALCITICO,
        prnt='85.00', teor_cao='45.00', teor_mgo='2.00',
    )
