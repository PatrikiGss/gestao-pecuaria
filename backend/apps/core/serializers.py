from rest_framework import serializers
from .models import Usuario, Produtor, Propriedade, Laboratorio, Cultura, AnaliseSolo, Recomendacao

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

class ProdutorSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Produtor
        fields = '__all__'

class PropriedadeSerializer(serializers.ModelSerializer):
    produtor = serializers.PrimaryKeyRelatedField(queryset=Produtor.objects.all(), required=False)

    class Meta:
        model = Propriedade
        fields =  '__all__'  

    def validate_produtor(self, value):
        request = self.context['request']
        if value and value.usuario != request.user:
            raise serializers.ValidationError("O produtor selecionado não pertence ao usuário logado.")
        return value


class LaboratorioSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Laboratorio
        fields = '__all__'

class CulturaSerializer(serializers.ModelSerializer):
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Cultura
        fields = '__all__'

class AnaliseSoloSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnaliseSolo
        fields = '__all__'
    def validate_campos(self, value):
        request = self.context['request']
        if value and value.usuario != request.user:
            raise serializers.ValidationError("Os campos selecionados não pertence ao usuário logado.")
        return value

class RecomendacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recomendacao
        fields = '__all__'
    def validate_analise(self, value):
        request = self.context['request']
        if value and value.usuario != request.user:
            raise serializers.ValidationError("a analise de solo selecionada não pertence ao usuário logado.")
        return value