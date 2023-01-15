from django.contrib import admin

from bot.models import TgUser


# Register your models here.
@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    """Класс модели для корректного отображения полей бота в Админ панели"""
    list_display = ('tg_chat_id', 'tg_username', 'user')
    read_only_fields = ('tg_chat_id', 'verification_code')
