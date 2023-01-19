from typing import Any

from django.conf import settings
from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import GetUpdatesResponse
from goals.models import (
    BoardParticipant,
    Goal,
    GoalCategory
)


class Command(BaseCommand):
    """Базовый класс для запуска и управления ботом"""
    help = "run bot"

    def __init__(self, *args, **kwargs):
        self.response: GetUpdatesResponse
        self.chat_id: int
        self.tg_user_id: int
        self.message: str
        self.message_id: int = 0
        self.user: TgUser = None
        self.category: GoalCategory
        self.goal: Goal
        self.reply_required: bool = False
        self.category_mode: bool = False
        self.goal_mode: bool = False
        self.offset = 0
        self.tg_client = TgClient(settings.TOKEN_TG_BOT)
        super().__init__(*args, **kwargs)

    def _get_response(self) -> None:
        """Ручка для получения ключевых данные из ответа"""
        # получить ключевые данные из ответа
        self.response = self.tg_client.get_updates(offset=self.offset)

        for item in self.response.result:
            self.offset = item.update_id + 1
            self.chat_id = item.message.chat.id
            self.tg_user_id = item.message.from_.id
            self.message = item.message.text

            self.user = TgUser.objects.filter(
                tg_user_id=self.tg_user_id, user_id__isnull=False
            ).first()

            # проверка на новость сообщения
            if not self.message_id == item.message.message_id:
                self.reply_required = True

            self.message_id = item.message.message_id

    def _main_logic(self) -> str:
        """Ручка для работы с верифицированным пользователем.
        Принимает и обрабатывает следующие командыЖ
        - /goals -> выводит список целей
        - /create -> позволяет создавать новые цели
        - /cancel -> позволяет отменить создание цели (только на этапе создания)"""

        if self.category_mode:
            reply = self._choose_category()
        elif self.goal_mode:
            reply = self._create_goal()
        # key commands
        elif self.message == '/start':
            reply: Any = 'Телеграм бот для просмотра и создания целей ' \
                         'на сайте http://larin.ga \n' \
                         ' Возможные команды: \n' \
                         '/start - стартовая информация для о боте \n' \
                         '/goals - просмотр списка имеющихся целей \n' \
                         '/create - создание цели в выбранной категории \n' \
                         '/cancel - отмена текущего действия \n'

        elif self.message == '/goals':
            reply = self._goals()
        elif self.message == '/create':
            reply = self._create()
        elif self.message == '/cancel':
            self.category_mode = False
            self.goal_mode = False
            reply: Any = 'Текущая операция прервана, введите новую команду. \n' \
                         '/start - стартовая информация для о боте \n' \
                         '/goals - просмотр списка имеющихся целей \n' \
                         '/create - создание цели в выбранной категории \n' \

        else:
            reply = 'Неизвестная команда'

        return reply

    def _verify(self) -> str:
        """Ручка для работы с не идентифицированными пользователями: генерация кода верификации
        и отправка его пользователю"""
        self.user = TgUser.objects.filter(tg_user_id=self.tg_user_id).first()
        if not self.user:
            self.user = TgUser.objects.create(
                tg_user_id=self.tg_user_id,
                tg_chat_id=self.chat_id)
            self.user.generate_verification_code()
            self.user.save()

        reply = (
            f"Подтвердите, пожалуйста, свой аккаунт.\n"
            f"Для подтверждения необходимо ввести код: {self.user.verification_code} на сайте http://larin.ga/auth ")

        return reply

    def _goals(self) -> list:
        """Ручка для получения и вывода списка категорий целей"""
        goals = Goal.objects.filter(
            category__board__participants__user=self.user.user, category__is_deleted=False
        ).only('id', 'title').exclude(status=Goal.Status.archived).order_by('created')

        prefix = ['Cписок ваших целей:']
        reply = [f'Цель №{goal.id}  "{goal.title}" из категории {goal.category}' for goal in goals]
        return prefix + reply

    def _create(self) -> list:
        """Ручка для получения и вывода списка категорий целей"""
        categories = GoalCategory.objects.filter(
            board__participants__user=self.user.user,
            board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
            is_deleted=False
        ).only('id', 'title')
        self.category_mode = True
        prefix = ['Введите номер категории из списка доступных:']
        reply = [f'#{category.id} {category.title}' for category in categories]
        return prefix + reply

    def _choose_category(self) -> str:
        """Ручка для выбора и валидации выбранной категорий для создания новой цели"""

        if not self.message.isnumeric():
            return 'Выбрана неверная категория'

        self.category = GoalCategory.objects.filter(
            pk=self.message,
            board__participants__user=self.user.user,
            board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
            is_deleted=False
        ).first()

        if not self.category:
            reply = 'Выбрана неверная категория'
        else:
            reply = (f'Выбрана категория {self.category.title}. \n '
                     f'Введите цель')
            self.goal_mode = True
            self.category_mode = False

        return reply

    def _create_goal(self) -> str:
        """Ручка для создания новой цели"""
        self.goal = Goal.objects.create(
            user=self.user.user, title=self.message, category=self.category
        )
        self.goal_mode = False
        return f'Ваша цель №{self.goal.id}   {self.goal.title}   успешно создана:\n ' \
               f'http://larin.ga/boards/{self.category.board.id}/goals?goal={self.goal.id}'

    def _send_reply(self, reply: str | list) -> None:
        """Ручка для отправки ответа"""
        if isinstance(reply, list):
            for item in reply:
                self.tg_client.send_message(chat_id=self.chat_id, text=item)
        else:
            self.tg_client.send_message(chat_id=self.chat_id, text=reply)

    def handle(self, *args, **options):
        """Ручка проверяет обновления чата. При получении новых сообщений от пользователей
                отправляет их на ручку -> _main_logic()  - уже был в боте, _verify() - не был в боте"""
        while True:
            self._get_response()

            if self.reply_required:
                if self.user:
                    reply = self._main_logic()
                else:
                    reply = self._verify()

                self._send_reply(reply=reply)
                self.reply_required = False
