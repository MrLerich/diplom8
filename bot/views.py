from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bot.models import TgUser
from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient
from todolist import settings


class BotVerifyView(generics.UpdateAPIView):
    """Вьюха для указания кода верификации бота"""
    model = TgUser
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']
    serializer_class = TgUserSerializer

    def patch(self, request, *args, **kwargs):
        """Для редактирования поля verification_code пользователя"""
        data = self.serializer_class(request.data).data
        tg_client = TgClient(settings.TOKEN_TG_BOT)
        tg_user = TgUser.objects.filter(verification_code=data['verification_code']).first()
        if not tg_user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        tg_user.user = request.user
        tg_user.save()
        tg_client.send_message(chat_id=tg_user.tg_chat_id, text='Вход прошел успешно!')
        return Response(data=data, status=status.HTTP_201_CREATED)
