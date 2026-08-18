from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from .serializers import UsuarioSerializer, UpdateUsuarioSerializer, GetUsuarioSerializer, ChangePasswordSerializer
from .models import Usuario

class RegisterView(APIView):
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        serializer.save()  
        return Response(serializer.data)  

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
    permission_classes = (IsAuthenticated,) 

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():  
            user = request.user 
            user.set_password(serializer.validated_data['new_password'])  
            user.save()  
            return Response({"detail": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


