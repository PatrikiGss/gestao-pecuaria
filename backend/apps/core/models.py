from django.db import models
from autenticacao.models import Usuario # pylint: disable=no-member

class Produtor(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=11, unique=True)
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    objects = models.Manager()

    class Meta:
        verbose_name = "Produtor"
        verbose_name_plural = "Produtores"

    def __str__(self):
        return str(self.nome)

class Propriedade(models.Model):
    produtor = models.ForeignKey(Produtor, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    
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
    estado = models.CharField(max_length=2)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    objects = models.Manager()

    class Meta:
        verbose_name = "Laboratório"
        verbose_name_plural = "Laboratórios"

    def __str__(self):
        return str(self.nome)


class Cultura(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Cultura"
        verbose_name_plural = "Culturas"

    def __str__(self):
        return str(self.nome)

class AnaliseSolo(models.Model):
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE)
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    cultura = models.ForeignKey(Cultura, on_delete=models.CASCADE)
    data = models.DateField()
    gleba = models.CharField(max_length=255)
    area = models.DecimalField(max_digits=10, decimal_places=2)
    laudo = models.TextField()
    ph_h2o = models.DecimalField(max_digits=5, decimal_places=2)
    s = models.DecimalField(max_digits=5, decimal_places=2)
    p = models.DecimalField(max_digits=5, decimal_places=2)
    k = models.DecimalField(max_digits=5, decimal_places=2)
    ca = models.DecimalField(max_digits=5, decimal_places=2)
    mg = models.DecimalField(max_digits=5, decimal_places=2)
    na = models.DecimalField(max_digits=5, decimal_places=2)
    al = models.DecimalField(max_digits=5, decimal_places=2)
    h = models.DecimalField(max_digits=5, decimal_places=2)
    materia_organica = models.DecimalField(max_digits=5, decimal_places=2)
    areia = models.DecimalField(max_digits=5, decimal_places=2)
    silte = models.DecimalField(max_digits=5, decimal_places=2)
    argila = models.DecimalField(max_digits=5, decimal_places=2)
    mn = models.DecimalField(max_digits=5, decimal_places=2)
    fe = models.DecimalField(max_digits=5, decimal_places=2)
    cu = models.DecimalField(max_digits=5, decimal_places=2)
    zn = models.DecimalField(max_digits=5, decimal_places=2)
    b = models.DecimalField(max_digits=5, decimal_places=2)
    
    objects = models.Manager()

    class Meta:
        verbose_name = "Análise de Solo"
        verbose_name_plural = "Análises de Solo"

    def __str__(self):
        return f"Análise de Solo de {self.propriedade.nome} - {self.data}"  # pylint: disable=no-member

class Recomendacao(models.Model):
    analise_solo = models.ForeignKey(AnaliseSolo, on_delete=models.CASCADE)
    camada_correcao = models.CharField(max_length=255)
    calcario_calcitico = models.DecimalField(max_digits=5, decimal_places=2)
    calcario_dolomitico = models.DecimalField(max_digits=5, decimal_places=2)
    calcario_magnesiano = models.DecimalField(max_digits=5, decimal_places=2)
    gesso = models.DecimalField(max_digits=5, decimal_places=2)
    kcl = models.DecimalField(max_digits=5, decimal_places=2)
    p2o5 = models.DecimalField(max_digits=5, decimal_places=2)
    n = models.DecimalField(max_digits=5, decimal_places=2)
    s = models.DecimalField(max_digits=5, decimal_places=2)
    
    objects = models.Manager()
    
    class Meta:
        verbose_name = "Recomendação"
        verbose_name_plural = "Recomendações"

    def __str__(self):
        return f"Recomendação para {self.analise_solo.propriedade.nome} - {self.analise_solo.data}"  # pylint: disable=no-member

