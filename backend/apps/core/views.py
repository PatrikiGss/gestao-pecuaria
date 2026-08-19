from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Usuario, Produtor, Propriedade, Laboratorio, Cultura, Calcario, Gleba, AnaliseSolo, Recomendacao
from .filtros import AnaliseSoloFilter, RecomendacaoFilter
from .serializers import (
    UsuarioSerializer,
    ProdutorSerializer,
    PropriedadeSerializer,
    LaboratorioSerializer,
    CulturaSerializer,
    CalcarioSerializer,
    GlebaSerializer,
    AnaliseSoloSerializer,
    RecomendacaoSerializer,
)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Usuario.objects.filter(id=self.request.user.id)


class ProdutorViewSet(viewsets.ModelViewSet):
    queryset = Produtor.objects.all()
    serializer_class = ProdutorSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ['usuario']
    ordering = ['nome']

    def get_queryset(self):
        return Produtor.objects.filter(usuario=self.request.user).order_by('nome')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)


class PropriedadeViewSet(viewsets.ModelViewSet):
    queryset = Propriedade.objects.all()
    serializer_class = PropriedadeSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ['produtor']
    ordering = ['nome']

    def get_queryset(self):
        return Propriedade.objects.filter(
            produtor__usuario=self.request.user
        ).select_related('produtor').order_by('nome')


class LaboratorioViewSet(viewsets.ModelViewSet):
    queryset = Laboratorio.objects.all()
    serializer_class = LaboratorioSerializer
    permission_classes = [IsAuthenticated]

    ordering = ['nome']

    def get_queryset(self):
        return Laboratorio.objects.filter(usuario=self.request.user).order_by('nome')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)


class CulturaViewSet(viewsets.ModelViewSet):
    queryset = Cultura.objects.all()
    serializer_class = CulturaSerializer
    permission_classes = [IsAuthenticated]

    ordering = ['nome']

    def get_queryset(self):
        return Cultura.objects.filter(usuario=self.request.user).order_by('nome')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)


class CalcarioViewSet(viewsets.ModelViewSet):
    queryset = Calcario.objects.all()
    serializer_class = CalcarioSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ['tipo']
    ordering = ['nome']

    def get_queryset(self):
        return Calcario.objects.filter(usuario=self.request.user).order_by('nome')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)


class GlebaViewSet(viewsets.ModelViewSet):
    queryset = Gleba.objects.all()
    serializer_class = GlebaSerializer
    permission_classes = [IsAuthenticated]

    # Substitui o filtro manual por query_params: o DjangoFilterBackend ja
    # entende '?propriedade=<id>', que e como a tela de analise monta a
    # lista em cascata.
    filterset_fields = ['propriedade']
    ordering = ['nome']

    def get_queryset(self):
        return Gleba.objects.filter(
            propriedade__produtor__usuario=self.request.user
        ).select_related('propriedade').order_by('nome')


class AnaliseSoloViewSet(viewsets.ModelViewSet):
    queryset = AnaliseSolo.objects.all()
    serializer_class = AnaliseSoloSerializer
    permission_classes = [IsAuthenticated]

    filterset_class = AnaliseSoloFilter
    # Mais recente primeiro: e o que interessa numa serie historica.
    ordering = ['-data']

    def get_queryset(self):
        # select_related evita uma consulta extra por linha ao montar o nome
        # da gleba e da propriedade na listagem.
        return AnaliseSolo.objects.filter(
            gleba__propriedade__produtor__usuario=self.request.user
        ).select_related(
            'gleba__propriedade', 'laboratorio', 'cultura'
        ).order_by('-data', '-id')


class RecomendacaoViewSet(viewsets.ModelViewSet):
    queryset = Recomendacao.objects.all()
    serializer_class = RecomendacaoSerializer
    permission_classes = [IsAuthenticated]

    filterset_class = RecomendacaoFilter
    ordering = ['-id']

    def get_queryset(self):
        return Recomendacao.objects.filter(
            analise_solo__gleba__propriedade__produtor__usuario=self.request.user
        ).select_related('analise_solo__gleba__propriedade').order_by('-id')
