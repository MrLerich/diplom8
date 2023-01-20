from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bot.models import TgUser
from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient
from todolist import settings


class VerificationView(GenericAPIView):
    """Ручка для указания кода верификации бота"""
    model = TgUser
    permission_classes = [IsAuthenticated]
    serializer_class = TgUserSerializer
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        """Метод для редактирования поля verification_code пользователя"""
        serializer: TgUserSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tg_user: TgUser = serializer.validated_data['tg_user']
        tg_user.user = self.request.user
        tg_user.save(update_fields=('user',))
        tg_client = TgClient(settings.TOKEN_TG_BOT)
        instance_serializer: TgUserSerializer = self.get_serializer(tg_user)
        tg_client.send_message(tg_user.tg_chat_id, 'Верификация прошла успешно! Введите /start для знакомства '
                                                   'с возможностями бота или /goals , '
                                                   'чтобы увидеть список своих целей.')
        return Response(instance_serializer.data)
