from rest_framework import serializers

from bot.models import TgUser


class TgUserSerializer(serializers.ModelSerializer):
    verification_code = serializers.CharField(write_only=True)

    class Meta:
        model = TgUser
        read_only_fields = ('tg_id', 'username', 'user_id')
        fields = ('tg_id', 'username', 'verification_code', 'user_id')
