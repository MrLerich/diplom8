from datetime import datetime

from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from goals.models import Goal, GoalCategory
from todolist import settings


class TgState:
    """Класс выбора состояния.
    Хранит в себе 3 состояния"""
    DEFAULT = 0
    CATEGORY_CHOOSE = 1
    GOAL_CREATE = 2

    def __init__(self, state, category_id=None):
        self.state = state  # при инициализации передаем какой-то state
        self.category_id = category_id
        # когда пользователь уже выбрал категорию ее нужно где-то хранить
        # для следующего обращения, чтобы создать цель

    def set_state(self, state):
        self.state = state

    def set_category_id(self, category_id):
        self.category_id = category_id


STATE = TgState(state=TgState.DEFAULT)  # инициализирую state телеги


class Command(BaseCommand):
    help = 'Runs telegram bot'
    tg_client = TgClient(settings.TOKEN_TG_BOT)

    def choose_category(self, msg: Message, tg_user: TgUser):
        """Выбираем списки категорий и отправляем тг бот"""
        goal_categories = GoalCategory.objects.filter(
            board__participants__user=tg_user.user,
            is_deleted=False,
        )
        goals_categories_str = '\n'.join(['-' + goal.title for goal in goal_categories])
        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f'Выберите категорию:\n {goals_categories_str}'
        )
        STATE.set_state(TgState.CATEGORY_CHOOSE)        # меняем стэйт из дефолта на выбор категорий

    def check_category(self, msg: Message):
        """Проверяет title категории кот прислал пользователь валидна"""
        category = GoalCategory.objects.filter(title=msg.text).first()
        if category:  # категория существует
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Введите название цели'
            )
            STATE.set_category_id(category.id)      # берем category_id и вызываем для дальнейшего создания цели
            STATE.set_state(TgState.GOAL_CREATE)        # меняет стэйт на сознание цели
        else:  # если категории нет
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Категории "{msg.text}" не существует'
            )

    def create_goal(self, msg: Message, tg_user: TgUser):
        """Создает цели"""
        category = GoalCategory.objects.get(pk=STATE.category_id)
        # Выбираем категорию для целей из state т.к. там уже id сохранили
        goal = Goal.objects.create(
            title=msg.text,
            user=tg_user.user,
            category=category,
            due_date=datetime.now().date(),
        )
        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f'Цель "{goal.title}" успешно создана!'
        )
        STATE.set_state(TgState.DEFAULT)        # после создания стейт снова меняем на дефолтный

    def get_goals(self, msg: Message, tg_user: TgUser):
        """Возвращает список целей без архивных"""
        goals = Goal.objects.filter(
            category__board__participants__user=tg_user.user,
        ).exclude(status=Goal.Status.archived)
        if goals.count() > 0:
            goals_str = '\n'.join([f'#{goal.id} {goal.title}' for goal in goals])
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Вот список ваших целей:\n {goals_str}'
            )
        else:
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'На данный момент у вас целей нет'
            )

    def cancel_operation(self, msg: Message):
        """Отменяем операцию"""
        STATE.set_state(TgState.DEFAULT)       # меняем статус на дефолтный
        self.tg_client.send_message(
            chat_id=msg.chat.id,
            text=f'Операция отменена',
        )

    def handle_message(self, msg: Message):
        # if TgUser нет то егл необходимо создать
        tg_user, created = TgUser.objects.get_or_create(
            tg_user_id=msg.msg_from.id,
            tg_chat_id=msg.chat.id,
        )  # возвращает (сущность, создана или нет) (instance, bool)
        if created:
            tg_user.generate_verification_code()
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Подтвердите свой аккаунт '
                     f'Для подтверждения необходимо ввести код: {tg_user.verification_code} на сайте'
            )
        if msg.text == '/goals':
            self.get_goals(msg, tg_user)        # возвращаем список целей
        elif msg.text == '/create':
            self.choose_category(msg, tg_user)
        elif msg.text == '/cancel':
            self.cancel_operation(msg)
        elif STATE.state == TgState.CATEGORY_CHOOSE:
            self.check_category(msg)
        elif STATE.state == TgState.GOAL_CREATE:
            self.create_goal(msg, tg_user)

        else:
            self.tg_client.send_message(
                chat_id=msg.chat.id,
                text=f'Неизвестная команд {msg.text}'
            )

    def handle(self, *args, **options):
        """Проверяет обновления чата. При получении новых сообщений от пользователей
                отправляет их на ручку -> handle_message"""
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                if hasattr(item, 'message'):  # message.item is not None есть ли атрибут message у этого item
                    self.handle_message(item.message)
