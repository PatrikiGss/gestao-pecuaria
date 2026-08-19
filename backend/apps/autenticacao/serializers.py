from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Cadastro publico (/autenticacao/signup/).

    Os campos sao listados um a um de proposito. Com 'fields = "__all__"' a
    lista incluia 'is_staff' e 'is_superuser', e como a RegisterView e aberta
    (AllowAny), qualquer POST anonimo com "is_superuser": true criava um
    administrador.
    """

    class Meta:
        model = Usuario
        fields = ['id', 'nome', 'email', 'cpf', 'telefone', 'creditos', 'password']
        # 'creditos' e exibido mas nao aceito na entrada: seu valor vem de
        # CREDITOS_INICIAIS (apps/autenticacao/models.py). Sem isso, qualquer
        # cadastro podia declarar o proprio saldo.
        read_only_fields = ['creditos']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class UpdateUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['nome', 'cpf', 'telefone', 'email']


class GetUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['nome', 'cpf', 'telefone', 'email']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
        return value

    def validate_new_password(self, value):
        # Sem isso a API aceitava trocar a senha por "123": os validadores de
        # AUTH_PASSWORD_VALIDATORS so rodam quando chamados explicitamente.
        validate_password(value, user=self.context['request'].user)
        return value

    def validate(self, attrs):
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError("A nova senha não pode ser igual à senha atual.")
        return attrs
