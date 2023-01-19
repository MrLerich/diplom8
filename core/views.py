from typing import Type

from django.contrib.auth import (
    get_user_model,
    login,
    logout
)
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models.manager import BaseManager
from rest_framework import (
    generics,
    permissions,
    status
)
from rest_framework.response import Response

from core.serializers import (
    LoginSerializer,
    ProfileSerializer,
    RegistrationSerializer,
    UpdatePasswordSerializer
)


USER_MODEL: Type[AbstractBaseUser] = get_user_model()


class RegistrationView(generics.CreateAPIView):     # generics. для того чтобы была лучше читабельность кода
    """вьюха регистрирует пользователя"""
    model = USER_MODEL
    serializer_class: Type[RegistrationSerializer] = RegistrationSerializer


class LoginView(generics.GenericAPIView):
    """вьюха логина пользователя"""
    serializer_class: Type[LoginSerializer] = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request=request, user=user)       # в сессию нужно залогиниться с нужными данными
        return Response(serializer.data)


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """вьюха для авторизованных пользователей показывает нужные поля(35ю4ю3)"""
    serializer_class: Type[ProfileSerializer] = ProfileSerializer
    queryset: BaseManager[AbstractBaseUser] = USER_MODEL.objects.all()
    permission_classes: list = [permissions.IsAuthenticated]

    def get_object(self):
        # т.к. нужен пользователь а не его id переписываем
        return self.request.user

    def delete(self, request, *args, **kwargs):     # 35.5.4 для логаута переопределили делит
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdatePasswordView(generics.UpdateAPIView):

    permission_classes: list = [permissions.IsAuthenticated]
    serializer_class: Type[UpdatePasswordSerializer] = UpdatePasswordSerializer

    def get_object(self):
        return self.request.user
