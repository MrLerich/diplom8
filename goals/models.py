from django.db import models


class DatesModelMixin(models.Model):
    """Базовая модель от которой наследуются остальные модели"""

    class Meta:
        abstract = True  # Помечаем класс как абстрактный – для него не будет таблички в БД
    # чтобы не повторяться в коде
    created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Дата последнего обновления', auto_now=True)


# Board
class Board(DatesModelMixin):
    """Класс модели доски целей"""

    class Meta:
        """Мета-класс для корректного отображение названия модели в админ панели"""
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'

    title = models.CharField(verbose_name='Название', max_length=255)
    is_deleted = models.BooleanField(verbose_name='Удалена', default=False)


# BoardParticipant
class BoardParticipant(DatesModelMixin):
    """Класс модели добавленных участников доски целей"""

    class Meta:
        """Мета-класс для корректного отображение названия модели в админ панели"""
        unique_together = ('board', 'user')
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'

    class Role(models.IntegerChoices):
        """Роли добавленных участников доски целей"""
        owner = 1, 'Владелец'
        writer = 2, 'Редактор'
        reader = 3, 'Читатель'

    editable_choices = Role.choices
    editable_choices.pop(0)

    board = models.ForeignKey(
        Board,
        verbose_name='Доска',
        on_delete=models.PROTECT,
        related_name='participants',
    )
    user = models.ForeignKey(
        'core.User',
        verbose_name='Пользователь',
        on_delete=models.PROTECT,
        related_name='participants',
    )
    role = models.PositiveSmallIntegerField(
        verbose_name='Роль',
        choices=Role.choices,
        default=Role.owner
    )


class GoalCategory(DatesModelMixin):
    """Модель Категории для целей"""

    class Meta:
        """Мета-класс для корректного отображение названия модели в админ панели"""
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    board = models.ForeignKey(
        'Board',
        verbose_name='Доска',
        on_delete=models.PROTECT,
        related_name='categories')
    title = models.CharField(verbose_name='Название', max_length=255)
    user = models.ForeignKey('core.User',
                             verbose_name='Автор',
                             on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name='Удалена', default=False)

    def __str__(self):
        return self.title


class Goal(DatesModelMixin):
    """Класс модели целей"""

    class Meta:
        """Мета-класс для корректного отображение названия модели в админ панели"""
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    class Status(models.IntegerChoices):
        """Класс модели для выбора статуса цели"""
        to_do = 1, 'К выполнению'
        in_progress = 2, 'В процессе'
        done = 3, 'Выполнено'
        archived = 4, 'Архив'

    class Priority(models.IntegerChoices):
        """Класс модели для выбора приоритета цели"""
        low = 1, 'Низкий'
        medium = 2, 'Средний'
        high = 3, 'Высокий'
        critical = 4, 'Критический'

    title = models.CharField(verbose_name='Название', max_length=255)
    description = models.TextField(verbose_name='Описание')
    status = models.PositiveSmallIntegerField(verbose_name='Статус',
                                              choices=Status.choices,
                                              default=Status.to_do)
    priority = models.PositiveSmallIntegerField(verbose_name='Приоритет',
                                                choices=Priority.choices,
                                                default=Priority.medium)
    due_date = models.DateField(verbose_name='Дата выполнения',
                                null=True)
    user = models.ForeignKey('core.User',
                             verbose_name='Автор',
                             on_delete=models.PROTECT)
    category = models.ForeignKey('GoalCategory',
                                 verbose_name='Категория',
                                 related_name='goals',
                                 on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class GoalComment(DatesModelMixin):
    """Класс модели комментариев цели"""

    class Meta:
        """Мета-класс для корректного отображение названия модели в админ панели"""
        verbose_name = 'Комментарий к цели'
        verbose_name_plural = 'Комментарии к цели'

    goal = models.ForeignKey(Goal,
                             verbose_name='Цель',
                             on_delete=models.PROTECT,
                             related_name='goal_comments')
    user = models.ForeignKey('core.User',
                             verbose_name='Автор',
                             on_delete=models.PROTECT,
                             related_name='goal_comments')
    text = models.TextField(verbose_name='Текст комментария')

    def __str__(self):
        return self.text
