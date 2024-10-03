from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields="__all__"
        extra_kwargs={
            'password': {'write_only': True}
        }
def create (self, validated_data):
    password = validated_data.pop('password')
    usuario = Usuario(**validated_data)
    usuario.set_password(password)
    usuario.save()
    return usuario
    