from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.crypto import get_random_string


class TgUser(models.Model):
    tg_user_id = models.BigIntegerField(unique=True)        # id из телеги
    tg_chat_id = models.BigIntegerField()
    username = models.CharField(max_length=32, validators=[MinLengthValidator(5)])
    # ограничения из документации телеги
    user = models.ForeignKey('core.User', null=True, on_delete=models.PROTECT)
    verification_code = models.CharField(max_length=10, unique=True)

    def generate_verification_code(self) -> str:
        code = get_random_string(10)
        self.verification_code = code
        self.save()
        return code

    class Meta:
        verbose_name = "Telegram пользователь"
        verbose_name_plural = "Telegram пользователи"