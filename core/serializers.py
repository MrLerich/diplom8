from typing import Type

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from rest_framework import serializers, exceptions

USER_MODEL: Type[AbstractBaseUser] = get_user_model()  # чтобы избежать циклического импорта


class RegistrationSerializer(serializers.ModelSerializer):
    '''регистрирует с проверкой правильности написания пароля'''
    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)

    def create(self, validated_data) -> USER_MODEL:
        password = validated_data.get('password')  # вариант validated_data['password'], сам пароль нужно внести в базу
        password_repeat = validated_data.pop(
            'password_repeat')  # password_repeat не нужен в базе, pop удаляет из справочника и возращает

        if password != password_repeat:
            raise serializers.ValidationError('Пароли не совпадают')

        hashed_password: str = make_password(password)  # чтобы не хранить в базе в открытом видк пароль - его хэшируем
        validated_data['password'] = hashed_password
        instance = super().create(validated_data)
        return instance

    class Meta:
        model: Type[AbstractBaseUser] = USER_MODEL
        fields: str = '__all__'


class LoginSerializer(serializers.ModelSerializer):
    '''логинит пользователя с username и password,
    С помощью механизма django.contrib.auth.authenticate проверяет
    корректность username/password(35.3.2)'''
    username: str = serializers.CharField(required=True)
    password: str = serializers.CharField(required=True, write_only=True)

    class Meta:
        model: Type[AbstractBaseUser] = USER_MODEL
        fields: list[str] = ['username', 'password']

    def create(self, validated_data) -> AbstractBaseUser:
        user: AbstractBaseUser | None = authenticate(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        if not user:
            raise exceptions.AuthenticationFailed
        return user


class ProfileSerializer(serializers.ModelSerializer):
    '''возвращает нужные нам поля из нашей USER_MODEL'''
    class Meta:
        model: Type[AbstractBaseUser] = USER_MODEL
        fields: list[str] = ['id', 'username', 'first_name', 'last_name', 'email']


class UpdatePasswordSerializer(serializers.Serializer):
    '''меняет/обновляет пароли, с проверкой валидности пароля'''
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault())  # из текущего реквеста забирает пользователя
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        '''проверять надежность пароля
            new_password с помощью встроенной проверки в Django'''
        user = attrs['user']
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({'old_password': 'incorrect password'})
        return attrs

    def update(self, instance, validated_data):
        instance.password = make_password(validated_data['new_password'])  # создаем новый пароль
        instance.save()  # тут уже его сохраняем
        return instance
