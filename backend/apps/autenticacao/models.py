from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from validadores import validar_cpf, validar_telefone


# ---------------------------------------------------------------------------
# CREDITOS
#
# Saldo fixo atribuido a toda conta nova. O campo existe por requisito do
# projeto, mas nenhuma regra de negocio o consome ainda: nada debita e nada
# bloqueia por saldo. Enquanto for assim ele e somente-leitura na API - antes
# desta mudanca o proprio usuario editava o proprio saldo.
#
# PARA MUDAR O VALOR
#   Altere a constante abaixo e rode:
#       python manage.py makemigrations && python manage.py migrate
#   A migracao gerada e um AlterField simples, nao toca nos dados. Contas ja
#   existentes mantem o saldo atual; o valor novo vale para as proximas.
#
# PARA VOLTAR A PERMITIR EDICAO
#   1. Remova 'creditos' de read_only_fields em apps/autenticacao/serializers.py
#      e em apps/core/serializers.py.
#   2. Reponha o campo nos formularios de TelaCadastro.vue e TelaUsuario.vue.
# ---------------------------------------------------------------------------
CREDITOS_INICIAIS = 0


class UsuarioManager(BaseUserManager):
    """
    Manager do Usuario.

    O UserManager padrao do Django exige 'username' como argumento posicional,
    mas este model removeu esse campo (username = None) e autentica por email.
    Sem este manager, 'manage.py createsuperuser' quebra com TypeError.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("O email e obrigatorio.")
        email = self.normalize_email(email)
        # 'creditos' nao precisa de setdefault aqui: o proprio campo do model
        # ja usa CREDITOS_INICIAIS como padrao, e duplicar o valor criaria uma
        # segunda fonte da verdade para mudar depois.
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superusuario precisa ter is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superusuario precisa ter is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=16, unique=True, validators=[validar_cpf])
    email = models.EmailField(unique=True)
    # 20 acompanha o Produtor.telefone; com 15 um telefone formatado
    # com DDI nao cabia aqui mas cabia la.
    telefone = models.CharField(max_length=20, validators=[validar_telefone])
    # Valor fixo: veja o bloco CREDITOS no topo deste arquivo.
    creditos = models.IntegerField(default=CREDITOS_INICIAIS)

    username = None
    USERNAME_FIELD = 'email'
    # Campos que o 'createsuperuser' pede alem do email/senha.
    # 'cpf' e unique, entao precisa ser preenchido: deixar em branco
    # impediria criar um segundo superusuario.
    REQUIRED_FIELDS = ['nome', 'cpf']

    objects = UsuarioManager()

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return str(self.nome)