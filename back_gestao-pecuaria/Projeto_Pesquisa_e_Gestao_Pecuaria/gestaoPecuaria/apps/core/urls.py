from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, ProdutorViewSet, PropriedadeViewSet, LaboratorioViewSet, CulturaViewSet, AnaliseSoloViewSet, RecomendacaoViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),# Para obter o token JWT
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),# Para atualizar o token JWT
]
