from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.crypto import get_random_string


class TgUser(models.Model):
    """Класс модели для пользователя бота"""
    tg_chat_id = models.BigIntegerField(verbose_name='Chat ID', unique=True)
    tg_user_id = models.BigIntegerField(verbose_name='Tg User ID', unique=True)
    tg_username = models.CharField(verbose_name='Tg Username',
                                   max_length=32,
                                   validators=[MinLengthValidator(5)],
                                   null=True,
                                   blank=True,
                                   default=None)
    user = models.ForeignKey('core.User',
                             verbose_name='User',
                             on_delete=models.CASCADE,
                             null=True,
                             default=None)
    verification_code = models.CharField(max_length=10,
                                         verbose_name='Код подтверждения',
                                         unique=True)

    def generate_verification_code(self) -> str:
        code = get_random_string(10)
        self.verification_code = code
        self.save()
        return code

    class Meta:
        verbose_name = 'Телеграм пользователь'
        verbose_name_plural = 'Телеграм пользователи'
