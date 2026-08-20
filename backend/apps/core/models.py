from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.functions import Lower
from validadores import UFS, validar_cpf, validar_telefone, validar_data_nao_futura
from autenticacao.models import Usuario # pylint: disable=no-member

# Nutrientes e fracoes nao podem ser negativos. Antes o banco aceitava pH -5.
NAO_NEGATIVO = [MinValueValidator(Decimal('0'))]

class Produtor(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    # 16 posicoes acompanham o Usuario.cpf e cabem o CPF formatado (14).
    cpf = models.CharField(max_length=16, validators=[validar_cpf])
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, validators=[validar_telefone])
    email = models.EmailField()

    objects = models.Manager()

    class Meta:
        verbose_name = "Produtor"
        verbose_name_plural = "Produtores"
        # A unicidade e por usuario, nao global. Com unique=True no campo, o
        # primeiro usuario a cadastrar um CPF impedia todos os demais de
        # cadastrarem o mesmo produtor, o que quebra o isolamento entre contas.
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'cpf'], name='produtor_cpf_unico_por_usuario'
            ),
            models.UniqueConstraint(
                fields=['usuario', 'email'], name='produtor_email_unico_por_usuario'
            ),
        ]

    def __str__(self):
        return str(self.nome)

class Propriedade(models.Model):
    produtor = models.ForeignKey(Produtor, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(Decimal('-180')), MaxValueValidator(Decimal('180'))],
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(Decimal('-90')), MaxValueValidator(Decimal('90'))],
    )
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=UFS)
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Propriedade"
        verbose_name_plural = "Propriedades"

    def __str__(self):
        return str(self.nome)


class Laboratorio(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=UFS)
    telefone = models.CharField(max_length=20, validators=[validar_telefone])
    email = models.EmailField()

    objects = models.Manager()

    class Meta:
        verbose_name = "Laboratório"
        verbose_name_plural = "Laboratórios"
        # Mesmo motivo do Produtor: dois usuarios podem cadastrar o mesmo
        # laboratorio, entao a unicidade e por conta.
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'email'], name='laboratorio_email_unico_por_usuario'
            ),
        ]

    def __str__(self):
        return str(self.nome)


class Cultura(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)

    # Saturacao por bases desejada (V2) para esta cultura, em %.
    #
    # E o alvo que entra na formula da calagem:
    #     NC = T x (V2 - V1) / 100 x (100 / PRNT)
    # onde V1 e a saturacao atual, calculada da analise.
    #
    # Fica opcional de proposito: uma cultura sem V2 definido simplesmente nao
    # tem calagem calculada, em vez de usar um valor arbitrario. Adubar por um
    # alvo que ninguem escolheu seria pior do que nao calcular.
    #
    # O valor varia por cultura e por fonte de referencia (Boletim 100 do IAC,
    # 5a Aproximacao de MG, Embrapa Cerrados). Cadastre conforme a fonte
    # adotada por quem assina o laudo.
    saturacao_bases_desejada = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name='Saturação por bases desejada (V₂) em %',
    )

    # ------------------------------------------------------------------
    # Parametros de adubacao.
    #
    # Sao eles que permitem a Recomendacao ser inteiramente calculada, sem
    # ninguem digitar dose. Cada um vem da fonte de referencia adotada - o
    # sistema aplica, nao arbitra.
    #
    # Ficam opcionais: uma cultura sem parametro simplesmente nao tem aquela
    # dose calculada, e a Recomendacao informa o que falta. E melhor deixar
    # em branco e dizer por que do que preencher com um numero sem lastro.
    # ------------------------------------------------------------------

    # Participacao de K na CTC que se quer atingir (tipicamente 3% a 5%).
    # A dose de potassio sai da diferenca entre esse alvo e o teor atual.
    saturacao_k_desejada = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name='Saturação de K na CTC desejada (%)',
    )

    # Teor de fosforo que se quer atingir no solo, em mg/dm3.
    fosforo_desejado = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Fósforo desejado (mg/dm³)',
    )

    # Quanto de P2O5 e preciso aplicar para elevar 1 mg/dm3 de P no solo.
    # Varia com a textura, porque solo argiloso fixa mais fosforo.
    fator_fixacao_fosforo = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='kg de P₂O₅ por mg/dm³ de P a elevar',
    )

    # Nitrogenio NAO se calcula a partir da analise de solo: depende da
    # cultura e da produtividade esperada. Entra aqui como dose da fonte.
    nitrogenio_recomendado = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Nitrogênio recomendado (kg/ha)',
    )

    # Enxofre: teor minimo desejado no solo, em mg/dm3.
    enxofre_desejado = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='Enxofre desejado (mg/dm³)',
    )

    objects = models.Manager()

    class Meta:
        verbose_name = "Cultura"
        verbose_name_plural = "Culturas"
        constraints = [
            models.UniqueConstraint(
                Lower('nome'), 'usuario', name='cultura_unica_por_usuario'
            ),
        ]

    def save(self, *args, **kwargs):
        self.nome = ' '.join(self.nome.split())
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.nome)


class Calcario(models.Model):
    """
    Corretivo cadastrado pelo usuario, com seu poder de neutralizacao.

    O PRNT e o que converte a necessidade teorica de calagem em dose real de
    produto: dois calcarios com PRNT diferente exigem quantidades diferentes
    para o mesmo efeito. Sem esse cadastro a formula fica pela metade.
    """

    CALCITICO = 'calcitico'
    MAGNESIANO = 'magnesiano'
    DOLOMITICO = 'dolomitico'
    TIPOS = [
        (CALCITICO, 'Calcítico (MgO abaixo de 5%)'),
        (MAGNESIANO, 'Magnesiano (MgO entre 5% e 12%)'),
        (DOLOMITICO, 'Dolomítico (MgO acima de 12%)'),
    ]

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255, help_text='Ex: Calcário dolomítico - Fornecedor X')
    tipo = models.CharField(max_length=20, choices=TIPOS)

    # PRNT = Poder Relativo de Neutralizacao Total, em %. Vem na embalagem.
    # Pode passar de 100 em corretivos muito reativos, por isso o teto e 150.
    prnt = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1')), MaxValueValidator(Decimal('150'))],
        verbose_name='PRNT (%)',
    )

    # Teores declarados na embalagem. Opcionais: servem para conferir se o tipo
    # informado bate com a composicao, e para estimar o aporte de Ca e Mg.
    teor_cao = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name='Teor de CaO (%)',
    )
    teor_mgo = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name='Teor de MgO (%)',
    )

    objects = models.Manager()

    class Meta:
        verbose_name = "Calcário"
        verbose_name_plural = "Calcários"
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                Lower('nome'), 'usuario', name='calcario_unico_por_usuario'
            ),
        ]

    def save(self, *args, **kwargs):
        self.nome = ' '.join(self.nome.split())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} (PRNT {self.prnt}%)"

class Gleba(models.Model):
    """
    Subdivisao de uma propriedade.

    Era um CharField livre dentro da AnaliseSolo. Como consequencia, "Talhao 3",
    "talhao 3" e "T3" viravam glebas distintas e a serie historica de um mesmo
    pedaco de terra se fragmentava - justamente o que da valor a uma sequencia
    de analises de solo.
    """

    propriedade = models.ForeignKey(
        Propriedade, on_delete=models.CASCADE, related_name='glebas'
    )
    nome = models.CharField(max_length=255)

    objects = models.Manager()

    class Meta:
        verbose_name = "Gleba"
        verbose_name_plural = "Glebas"
        ordering = ['nome']
        constraints = [
            # Lower() torna a unicidade insensivel a maiusculas: dentro da
            # mesma propriedade, "Talhao 3" e "talhao 3" passam a ser a mesma
            # gleba, e a segunda tentativa de cadastro e recusada.
            models.UniqueConstraint(
                Lower('nome'),
                'propriedade',
                name='gleba_unica_por_propriedade',
            ),
        ]

    def save(self, *args, **kwargs):
        # Normaliza espacos antes de gravar, para " Talhao  3 " nao escapar
        # da restricao de unicidade por causa de espaco extra.
        self.nome = ' '.join(self.nome.split())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.propriedade.nome}"  # pylint: disable=no-member


class AnaliseSolo(models.Model):
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    # A propriedade nao e mais guardada aqui: vem pela gleba. Manter as duas
    # permitia que se contradissessem (analise numa gleba da Fazenda A com
    # propriedade apontando para a Fazenda B).
    gleba = models.ForeignKey(Gleba, on_delete=models.PROTECT, related_name='analises')
    cultura = models.ForeignKey(Cultura, on_delete=models.CASCADE)
    data = models.DateField(validators=[validar_data_nao_futura])

    # Camada de solo amostrada.
    #
    # A formula da calagem e calibrada para a camada superficial (0-20 cm).
    # Sem este campo, uma analise de subsuperficie entraria na mesma conta e
    # produziria uma dose errada sem nenhum aviso. O padrao e 0-20 porque e a
    # amostragem usual para recomendacao de corretivo.
    CAMADA_0_20 = '0-20'
    CAMADA_20_40 = '20-40'
    CAMADA_40_60 = '40-60'
    CAMADA_OUTRA = 'outra'
    CAMADAS = [
        (CAMADA_0_20, '0 a 20 cm (superficial)'),
        (CAMADA_20_40, '20 a 40 cm (subsuperficial)'),
        (CAMADA_40_60, '40 a 60 cm'),
        (CAMADA_OUTRA, 'Outra'),
    ]
    camada = models.CharField(
        max_length=10, choices=CAMADAS, default=CAMADA_0_20,
        verbose_name='Camada amostrada',
    )
    area = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0'))]
    )
    laudo = models.TextField()
    ph_h2o = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('14'))],
    )
    s = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    p = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    k = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    ca = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    mg = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    na = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    al = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    h = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    materia_organica = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    areia = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    silte = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    argila = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    mn = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    fe = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    cu = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    zn = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    b = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Análise de Solo"
        verbose_name_plural = "Análises de Solo"

    def __str__(self):
        return f"Análise de Solo de {self.gleba} - {self.data}"  # pylint: disable=no-member

class Recomendacao(models.Model):
    analise_solo = models.ForeignKey(AnaliseSolo, on_delete=models.CASCADE)
    camada_correcao = models.CharField(max_length=255)
    calcario_calcitico = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    calcario_dolomitico = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    calcario_magnesiano = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    gesso = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    kcl = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    p2o5 = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    n = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    s = models.DecimalField(max_digits=8, decimal_places=2, validators=NAO_NEGATIVO)
    
    objects = models.Manager()
    
    class Meta:
        verbose_name = "Recomendação"
        verbose_name_plural = "Recomendações"

    def __str__(self):
        return f"Recomendação para {self.analise_solo.gleba} - {self.analise_solo.data}"  # pylint: disable=no-member

