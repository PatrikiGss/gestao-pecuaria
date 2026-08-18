from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario 
        fields = "__all__"  
        extra_kwargs = {
            'password': {'write_only': True}  
        }

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

    def validate(self, attrs):
        if attrs['old_password'] == attrs['new_password']: 
            raise serializers.ValidationError("A nova senha não pode ser igual à senha atual.")  
        return attrs  
