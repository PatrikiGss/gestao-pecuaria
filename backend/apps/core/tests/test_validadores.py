"""
Validadores de dominio.

Sao puros e nao precisam de banco, mas a checagem pela API tambem esta aqui:
declarar o validador no model nao basta se o serializer nao o aplicar, e a
diferenca entre as duas coisas nao aparece lendo o codigo.
"""
from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework import status

import validadores


class TestCPF:
    @pytest.mark.parametrize('cpf', [
        '52998224725',        # sem pontuacao
        '529.982.247-25',     # com pontuacao
        '153.509.460-56',
    ])
    def test_aceita_cpf_valido(self, cpf):
        validadores.validar_cpf(cpf)   # nao levanta

    @pytest.mark.parametrize('cpf, motivo', [
        ('12345678901', 'digitos verificadores errados'),
        ('529.982.247-24', 'ultimo digito trocado'),
        ('5299822472', 'so 10 digitos'),
        ('529982247255', '12 digitos'),
        ('', 'vazio'),
        ('abcdefghijk', 'sem numero nenhum'),
    ])
    def test_recusa_cpf_invalido(self, cpf, motivo):
        with pytest.raises(ValidationError):
            validadores.validar_cpf(cpf)

    @pytest.mark.parametrize('repetido', [
        '00000000000', '11111111111', '99999999999',
    ])
    def test_recusa_sequencia_repetida(self, repetido):
        """
        Sequencias como 111.111.111-11 PASSAM no calculo dos digitos
        verificadores - a conta fecha. Precisam ser barradas a parte, e por
        isso tem teste proprio: e o caso que um validador ingenuo deixa entrar.
        """
        with pytest.raises(ValidationError):
            validadores.validar_cpf(repetido)


class TestTelefone:
    @pytest.mark.parametrize('numero', [
        '4899990000',        # fixo com DDD, 10 digitos
        '48999900000',       # celular com DDD, 11 digitos
        '(48) 99990-0000',   # pontuacao ignorada
    ])
    def test_aceita_telefone_plausivel(self, numero):
        validadores.validar_telefone(numero)

    @pytest.mark.parametrize('numero', ['999900000', '489999000000', '', '12'])
    def test_recusa_quantidade_errada_de_digitos(self, numero):
        with pytest.raises(ValidationError):
            validadores.validar_telefone(numero)


class TestDataNaoFutura:
    def test_aceita_hoje(self):
        validadores.validar_data_nao_futura(timezone.localdate())

    def test_aceita_passado(self):
        validadores.validar_data_nao_futura(timezone.localdate() - timedelta(days=365))

    def test_recusa_amanha(self):
        with pytest.raises(ValidationError):
            validadores.validar_data_nao_futura(timezone.localdate() + timedelta(days=1))

    def test_hoje_acompanha_o_fuso_e_nao_o_relogio_do_sistema(self):
        """
        A divergencia e real e diaria: com date.today(), um servidor hospedado
        em UTC recusaria como futura uma data que o usuario no Brasil acabou de
        viver - das 21h a meia-noite.

        Verificado pelo COMPORTAMENTO, e nao lendo o codigo-fonte: dois fusos
        bem afastados (UTC+14 e UTC-11) enxergam datas diferentes no mesmo
        instante, e o validador tem que seguir o fuso configurado. Se ele
        estivesse lendo o relogio do sistema, as duas metades dariam igual.
        """
        adiantado = 'Pacific/Kiritimati'   # UTC+14
        atrasado = 'Pacific/Midway'        # UTC-11

        with timezone.override(adiantado):
            hoje_la = timezone.localdate()
        with timezone.override(atrasado):
            hoje_ca = timezone.localdate()

        assert hoje_la > hoje_ca, 'os dois fusos precisam estar em dias diferentes'

        # A data de 'hoje' no fuso adiantado ainda e futuro no atrasado.
        with timezone.override(adiantado):
            validadores.validar_data_nao_futura(hoje_la)   # aceita

        with timezone.override(atrasado):
            with pytest.raises(ValidationError):
                validadores.validar_data_nao_futura(hoje_la)


class TestSomaGranulometrica:
    @pytest.mark.parametrize('areia, silte, argila', [
        (25, 25, 50),        # porcentagem exata
        (250, 250, 500),     # g/kg
        (25.5, 25.0, 49.0),  # 99,5: dentro da folga de 2%
    ])
    def test_aceita_soma_coerente(self, areia, silte, argila):
        assert validadores.validar_soma_granulometrica(areia, silte, argila) is None

    @pytest.mark.parametrize('areia, silte, argila', [
        (100, 100, 100),     # 300: o caso que o banco aceitava
        (10, 10, 10),        # 30
        (500, 500, 500),     # 1500
    ])
    def test_recusa_soma_incoerente(self, areia, silte, argila):
        erro = validadores.validar_soma_granulometrica(areia, silte, argila)
        assert erro is not None
        assert '100' in erro and '1000' in erro

    def test_valor_ausente_nao_e_erro(self):
        # Faltando uma fracao nao da para somar; quem exige o campo e o model.
        assert validadores.validar_soma_granulometrica(25, None, 50) is None


class TestUFs:
    def test_tem_as_27_unidades(self):
        assert len(validadores.UFS) == 27

    def test_siglas_sao_unicas_e_de_duas_letras(self):
        siglas = [sigla for sigla, _ in validadores.UFS]
        assert len(set(siglas)) == 27
        assert all(len(s) == 2 and s.isupper() for s in siglas)


# ==========================================================================
# Os mesmos validadores, agora atraves da API
# ==========================================================================

@pytest.mark.django_db
class TestValidacaoChegaNaAPI:
    def test_cpf_invalido_e_recusado_no_cadastro_de_produtor(self, cliente):
        resposta = cliente.post('/produtores/', {
            'cpf': '11111111111', 'nome': 'Produtor', 'telefone': '4899990000',
            'email': 'p@exemplo.com',
        }, format='json')

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cpf' in resposta.data

    def test_estado_fora_das_27_ufs_e_recusado(self, cliente, cadastros):
        resposta = cliente.post('/propriedades/', {
            'produtor': cadastros['produtor'].pk, 'nome': 'Fazenda',
            'longitude': '-50.3', 'latitude': '-27.8', 'endereco': 'x',
            'cidade': 'Lages', 'estado': 'XX',
        }, format='json')

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert 'estado' in resposta.data

    def test_granulometria_incoerente_e_recusada(self, cliente, cadastros):
        # Validacao cruzada: nao cabe num validador de campo, que enxerga um
        # valor por vez. Antes o banco aceitava areia+silte+argila = 300%.
        payload = {
            'laboratorio': cadastros['laboratorio'].pk,
            'gleba': cadastros['gleba'].pk, 'cultura': cadastros['cultura'].pk,
            'data': '2024-05-10', 'camada': '0-20', 'area': '10.00',
            'laudo': 'L-1', 'ph_h2o': '5.5', 's': '8', 'p': '6', 'k': '0.15',
            'ca': '2.4', 'mg': '0.9', 'na': '0.02', 'al': '0.3', 'h': '3.5',
            'materia_organica': '2.8',
            'areia': '100', 'silte': '100', 'argila': '100',
            'mn': '8', 'fe': '30', 'cu': '1.2', 'zn': '2.1', 'b': '0.3',
        }
        resposta = cliente.post('/analisesolo/', payload, format='json')

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert {'areia', 'silte', 'argila'} & set(resposta.data)

    @pytest.mark.parametrize('campo, valor', [
        ('ph_h2o', '20'),    # pH so existe de 0 a 14
        ('ph_h2o', '-1'),
        ('ca', '-1'),        # antes o banco aceitava nutriente negativo
        ('argila', '-5'),
        ('area', '-10'),
    ])
    def test_valor_fora_da_faixa_e_recusado_pela_api(
            self, cliente, cadastros, campo, valor):
        payload = {
            'laboratorio': cadastros['laboratorio'].pk,
            'gleba': cadastros['gleba'].pk, 'cultura': cadastros['cultura'].pk,
            'data': '2024-05-10', 'camada': '0-20', 'area': '10.00',
            'laudo': 'L-1', 'ph_h2o': '5.5', 's': '8', 'p': '6', 'k': '0.15',
            'ca': '2.4', 'mg': '0.9', 'na': '0.02', 'al': '0.3', 'h': '3.5',
            'materia_organica': '2.8', 'areia': '40', 'silte': '25',
            'argila': '35', 'mn': '8', 'fe': '30', 'cu': '1.2', 'zn': '2.1',
            'b': '0.3',
        }
        payload[campo] = valor

        resposta = cliente.post('/analisesolo/', payload, format='json')

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert campo in resposta.data

    def test_data_futura_e_recusada_pela_api(self, cliente, cadastros):
        amanha = (timezone.localdate() + timedelta(days=1)).isoformat()
        payload = {
            'laboratorio': cadastros['laboratorio'].pk,
            'gleba': cadastros['gleba'].pk, 'cultura': cadastros['cultura'].pk,
            'data': amanha, 'camada': '0-20', 'area': '10.00',
            'laudo': 'L-1', 'ph_h2o': '5.5', 's': '8', 'p': '6', 'k': '0.15',
            'ca': '2.4', 'mg': '0.9', 'na': '0.02', 'al': '0.3', 'h': '3.5',
            'materia_organica': '2.8', 'areia': '40', 'silte': '25',
            'argila': '35', 'mn': '8', 'fe': '30', 'cu': '1.2', 'zn': '2.1',
            'b': '0.3',
        }
        resposta = cliente.post('/analisesolo/', payload, format='json')

        assert resposta.status_code == status.HTTP_400_BAD_REQUEST
        assert 'data' in resposta.data
