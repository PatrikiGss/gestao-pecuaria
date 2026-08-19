from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from validadores import validar_soma_granulometrica
from .agronomia import (
    diagnostico as calcular_diagnostico,
    recomendacao_calagem as calcular_calagem,
    classificar_saturacao_bases,
    classificar_saturacao_aluminio,
)
from .models import Usuario, Produtor, Propriedade, Laboratorio, Cultura, Calcario, Gleba, AnaliseSolo, Recomendacao


class DonoDoRecursoMixin:
    """
    Restringe as chaves estrangeiras ao que pertence ao usuario da requisicao.

    Sem isso, o PrimaryKeyRelatedField gerado pelo ModelSerializer aceita
    qualquer PK existente no banco, e um usuario consegue vincular registros
    seus a recursos de outro usuario (IDOR). Limitar o queryset faz o DRF
    responder 400 com "object does not exist" para PKs de terceiros.

    Cada subclasse declara em 'querysets_por_dono' uma funcao que recebe o
    usuario e devolve o queryset permitido para aquele campo.
    """

    querysets_por_dono = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return
        for campo, filtro in self.querysets_por_dono.items():
            if campo in self.fields:
                self.fields[campo].queryset = filtro(request.user)


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer do usuario autenticado (endpoint /usuarios/).

    Difere do autenticacao.UsuarioSerializer, usado no cadastro publico.
    Aqui os campos sao listados explicitamente para que 'is_staff',
    'is_superuser', 'groups' e 'user_permissions' fiquem fora da API: com
    'fields = __all__' o proprio usuario conseguia se promover a administrador
    num PUT do proprio registro.
    """

    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'cpf', 'telefone', 'creditos', 'password']
        # 'creditos' e exibido mas nao aceito na entrada: seu valor vem de
        # CREDITOS_INICIAIS (apps/autenticacao/models.py). Sem isso, o usuario
        # editava o proprio saldo num PUT do proprio registro.
        read_only_fields = ['creditos']
        extra_kwargs = {
            # write_only impede que o hash da senha volte no GET
            'password': {'write_only': True, 'required': False},
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'A senha e obrigatoria.'})
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        # set_password gera o hash; sem isso a senha ia crua para o banco
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class ProdutorSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Produtor
        fields = '__all__'


class PropriedadeSerializer(DonoDoRecursoMixin, serializers.ModelSerializer):
    querysets_por_dono = {
        'produtor': lambda user: Produtor.objects.filter(usuario=user),
    }

    class Meta:
        model = Propriedade
        fields = '__all__'


class LaboratorioSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Laboratorio
        fields = '__all__'


class NomeUnicoPorUsuarioMixin:
    """
    Recusa nome repetido dentro da mesma conta, sem diferenciar maiusculas.

    A restricao equivalente existe no banco. Sem esta checagem antes, a
    violacao subiria como IntegrityError - erro 500 - em vez de uma mensagem
    de validacao que o formulario consegue exibir no campo certo.
    """

    modelo_unico = None

    def validate_nome(self, value):
        nome = ' '.join((value or '').split())
        request = self.context.get('request')
        if not nome or request is None or not request.user.is_authenticated:
            return nome

        existentes = self.modelo_unico.objects.filter(
            usuario=request.user, nome__iexact=nome
        )
        if self.instance is not None:
            existentes = existentes.exclude(pk=self.instance.pk)
        if existentes.exists():
            raise serializers.ValidationError('Já existe um registro com esse nome.')
        return nome


class CulturaSerializer(NomeUnicoPorUsuarioMixin, serializers.ModelSerializer):
    modelo_unico = Cultura
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Cultura
        fields = '__all__'


class CalcarioSerializer(NomeUnicoPorUsuarioMixin, serializers.ModelSerializer):
    modelo_unico = Calcario
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    tipo_descricao = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Calcario
        fields = '__all__'

    def validate(self, attrs):
        # Coerencia entre o tipo informado e o teor declarado. A classificacao
        # brasileira separa os tres tipos justamente pela faixa de MgO, entao
        # divergencia aqui costuma ser erro de digitacao na embalagem.
        tipo = attrs.get('tipo', getattr(self.instance, 'tipo', None))
        mgo = attrs.get('teor_mgo', getattr(self.instance, 'teor_mgo', None))

        if tipo and mgo is not None:
            esperado = (
                Calcario.CALCITICO if mgo < 5
                else Calcario.MAGNESIANO if mgo <= 12
                else Calcario.DOLOMITICO
            )
            if tipo != esperado:
                rotulos = dict(Calcario.TIPOS)
                raise serializers.ValidationError({
                    'tipo': (
                        f'Um calcário com {mgo}% de MgO é classificado como '
                        f'"{rotulos[esperado]}". Confira o tipo ou o teor.'
                    )
                })
        return attrs


class GlebaSerializer(DonoDoRecursoMixin, serializers.ModelSerializer):
    querysets_por_dono = {
        'propriedade': lambda user: Propriedade.objects.filter(produtor__usuario=user),
    }
    propriedade_nome = serializers.CharField(source='propriedade.nome', read_only=True)

    class Meta:
        model = Gleba
        fields = ['id', 'nome', 'propriedade', 'propriedade_nome']

    def validate(self, attrs):
        # A restricao de unicidade e insensivel a maiusculas e vive no banco.
        # Sem esta checagem, a violacao subiria como IntegrityError (erro 500)
        # em vez de uma mensagem de validacao.
        nome = attrs.get('nome', getattr(self.instance, 'nome', ''))
        propriedade = attrs.get('propriedade', getattr(self.instance, 'propriedade', None))
        nome = ' '.join((nome or '').split())

        if nome and propriedade is not None:
            existentes = Gleba.objects.filter(propriedade=propriedade, nome__iexact=nome)
            if self.instance is not None:
                existentes = existentes.exclude(pk=self.instance.pk)
            if existentes.exists():
                raise serializers.ValidationError(
                    {'nome': 'Já existe uma gleba com esse nome nesta propriedade.'}
                )
        return attrs


class AnaliseSoloSerializer(DonoDoRecursoMixin, serializers.ModelSerializer):
    querysets_por_dono = {
        'laboratorio': lambda user: Laboratorio.objects.filter(usuario=user),
        'gleba': lambda user: Gleba.objects.filter(propriedade__produtor__usuario=user),
        'cultura': lambda user: Cultura.objects.filter(usuario=user),
    }
    # A propriedade nao e mais gravada na analise; vem pela gleba. Estes campos
    # de leitura evitam que o frontend precise cruzar listas para exibi-la.
    propriedade = serializers.PrimaryKeyRelatedField(
        source='gleba.propriedade', read_only=True
    )
    propriedade_nome = serializers.CharField(
        source='gleba.propriedade.nome', read_only=True
    )
    gleba_nome = serializers.CharField(source='gleba.nome', read_only=True)
    # Indices derivados (SB, CTC, V%, m%, relacoes, classe textural).
    #
    # Calculados a cada leitura em vez de gravados: sao funcao dos valores da
    # propria analise, e guardar copia abriria espaco para ficarem defasados
    # se algum valor de origem for corrigido depois.
    diagnostico = serializers.SerializerMethodField()
    # Recomendacao de calagem. Depende do V2 da cultura e, para a dose real,
    # do PRNT de um calcario - ambos cadastrados pelo usuario. Sem eles a
    # resposta traz o que consegue calcular e diz o que falta.
    calagem = serializers.SerializerMethodField()

    def get_diagnostico(self, obj):
        dados = calcular_diagnostico(obj)
        # Traduz os numeros centrais em faixa de leitura: "V% 45" diz pouco a
        # quem nao e da area, "Baixo" diz muito.
        dados['classificacao_v'] = classificar_saturacao_bases(dados['saturacao_bases'])
        dados['classificacao_m'] = classificar_saturacao_aluminio(dados['saturacao_aluminio'])
        return dados

    def get_calagem(self, obj):
        v2 = obj.cultura.saturacao_bases_desejada if obj.cultura_id else None

        # O PRNT vem do calcario indicado pela relacao Ca:Mg, entre os que o
        # usuario cadastrou. Sem cadastro, sai so a necessidade teorica.
        prnt = None
        calcario = None
        if obj.gleba_id:
            from .agronomia import tipo_calcario_indicado
            tipo = tipo_calcario_indicado(obj.ca, obj.mg)
            dono = obj.gleba.propriedade.produtor.usuario_id
            calcario = (
                Calcario.objects.filter(usuario_id=dono, tipo=tipo)
                .order_by('-prnt').first()
            )
            if calcario:
                prnt = calcario.prnt

        resultado = calcular_calagem(obj, v2=v2, prnt=prnt)
        if resultado.get('aplicavel'):
            resultado['calcario_sugerido'] = calcario.nome if calcario else None
            resultado['pendencias'] = [
                mensagem for condicao, mensagem in [
                    (v2 is None, f'A cultura "{obj.cultura.nome}" não tem V₂ cadastrado.'),
                    (prnt is None, 'Nenhum calcário cadastrado do tipo indicado.'),
                ] if condicao
            ]
        return resultado

    class Meta:
        model = AnaliseSolo
        fields = '__all__'

    def validate(self, attrs):
        # Validacao cruzada: as tres fracoes granulometricas repartem o mesmo
        # volume de solo, entao precisam somar o total. Nao cabe num validador
        # de campo, que enxerga um valor por vez - antes o banco aceitava
        # areia + silte + argila = 300%.
        def valor(campo):
            if campo in attrs:
                return attrs[campo]
            return getattr(self.instance, campo, None)

        erro = validar_soma_granulometrica(
            valor('areia'), valor('silte'), valor('argila')
        )
        if erro:
            raise serializers.ValidationError({'areia': erro, 'silte': erro, 'argila': erro})
        return attrs


class RecomendacaoSerializer(DonoDoRecursoMixin, serializers.ModelSerializer):
    querysets_por_dono = {
        'analise_solo': lambda user: AnaliseSolo.objects.filter(
            gleba__propriedade__produtor__usuario=user
        ),
    }
    # Campos de leitura para a listagem. Sem eles a tela precisaria carregar
    # todas as analises so para descobrir o laudo de cada recomendacao.
    analise_laudo = serializers.CharField(source='analise_solo.laudo', read_only=True)
    analise_data = serializers.DateField(source='analise_solo.data', read_only=True)
    gleba_nome = serializers.CharField(source='analise_solo.gleba.nome', read_only=True)

    class Meta:
        model = Recomendacao
        fields = '__all__'
