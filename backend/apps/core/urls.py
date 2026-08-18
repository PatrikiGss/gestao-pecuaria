from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, ProdutorViewSet, PropriedadeViewSet, LaboratorioViewSet, CulturaViewSet, AnaliseSoloViewSet, RecomendacaoViewSet


router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'produtores', ProdutorViewSet)
router.register(r'propriedades', PropriedadeViewSet)
router.register(r'laboratorios', LaboratorioViewSet)
router.register(r'culturas', CulturaViewSet)
router.register(r'analisesolo', AnaliseSoloViewSet)
router.register(r'recomendacoes', RecomendacaoViewSet)

app_name = 'core'

urlpatterns = [ 
    path('', include(router.urls)),
]
