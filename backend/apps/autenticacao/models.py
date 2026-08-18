from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


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
        extra_fields.setdefault('creditos', 0)
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
    cpf = models.CharField(max_length=16, unique=True)
    email = models.EmailField(unique=True) 
    telefone = models.CharField(max_length=15)
    creditos = models.IntegerField()

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