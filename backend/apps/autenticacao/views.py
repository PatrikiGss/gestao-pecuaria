from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .serializers import (
    UsuarioSerializer,
    UpdateUsuarioSerializer,
    GetUsuarioSerializer,
    ChangePasswordSerializer,
)
from .models import Usuario


def invalidar_tokens_do_usuario(user):
    """
    Manda para a blacklist todo refresh token ainda vivo do usuario.

    Usado na troca de senha: sem isso, uma sessao aberta antes da troca
    continuava valida, entao trocar a senha nao expulsava ninguem.
    """
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


class RegisterView(APIView):
    # Explicito para deixar claro que o cadastro e publico de proposito.
    # A protecao contra criacao de admin esta no UsuarioSerializer, que nao
    # expoe is_staff nem is_superuser.
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MeuPerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            user = Usuario.objects.get(pk=request.user.id)
        except Usuario.DoesNotExist:
            raise NotFound('Usuário não encontrado.')

        serializer = UpdateUsuarioSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get(self, request):
        try:
            user = Usuario.objects.get(pk=request.user.id)
        except Usuario.DoesNotExist:
            raise NotFound('Usuário não encontrado.')

        serializer = GetUsuarioSerializer(user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        invalidar_tokens_do_usuario(user)

        return Response(
            {"detail": "Senha alterada com sucesso. Faça login novamente."},
            status=status.HTTP_200_OK,
        )
