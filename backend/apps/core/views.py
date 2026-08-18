from django.forms import ValidationError
from rest_framework import viewsets
from django.db import models
from .models import Usuario,Produtor,Propriedade,Laboratorio,Cultura,AnaliseSolo,Recomendacao 
from .serializers import UsuarioSerializer,ProdutorSerializer,PropriedadeSerializer,LaboratorioSerializer,CulturaSerializer,AnaliseSoloSerializer,RecomendacaoSerializer
from rest_framework.permissions import IsAuthenticated


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class=UsuarioSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
         return Usuario.objects.filter(id=self.request.user.id)
    
    
class ProdutorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Produtor.objects.all()
    serializer_class = ProdutorSerializer

    def get_queryset(self):
        return Produtor.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)



class PropriedadeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Propriedade.objects.all()
    serializer_class = PropriedadeSerializer

    def get_queryset(self):
        return Propriedade.objects.filter(produtor__usuario=self.request.user)


class LaboratorioViewSet(viewsets.ModelViewSet):
    queryset=Laboratorio.objects.all()
    serializer_class=LaboratorioSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Laboratorio.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)


class CulturaViewSet(viewsets.ModelViewSet):
    queryset=Cultura.objects.all()
    serializer_class=CulturaSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Cultura.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)
    
class AnaliseSoloViewSet(viewsets.ModelViewSet):
    queryset=AnaliseSolo.objects.all()
    serializer_class=AnaliseSoloSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return AnaliseSolo.objects.filter(propriedade__produtor__usuario=self.request.user)


class RecomendacaoViewSet(viewsets.ModelViewSet):
    queryset=Recomendacao.objects.all()
    serializer_class= RecomendacaoSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Recomendacao.objects.filter(analise_solo__propriedade__produtor__usuario=self.request.user)


