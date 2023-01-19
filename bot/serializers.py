from typing import Any

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bot.models import TgUser


class TgUserSerializer(serializers.ModelSerializer):
    """Класс модели сериализатора пользователя бота"""
    verification_code = serializers.CharField(write_only=True)
    tg_chat_id = serializers.SlugField(source='chat_id', read_only=True)

    class Meta:
        """Мета-класс для указания модели для сериализатора, полей модели сериализатора,
                         и не изменяемых полей"""
        model = TgUser
        fields = ('tg_user_id', 'verification_code', 'tg_username', 'user_id', 'tg_chat_id')
        read_only_fields = ('tg_user_id', 'user_id', 'tg_username', 'tg_chat_id')

    def validate(self, attrs: dict[str, Any]):
        """Метод для валидации кода верификации"""
        verification_code = attrs.get('verification_code')
        tg_user = TgUser.objects.filter(verification_code=verification_code).first()
        if not tg_user:
            raise ValidationError('Invalid verification code')
        attrs['tg_user'] = tg_user
        return attrs
