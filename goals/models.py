from django.db import models


class DatesModelMixin(models.Model):
    class Meta:
        abstract = True  # Помечаем класс как абстрактный – для него не будет таблички в БД
    #чтобы не повторяться в коде
    created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Дата последнего обновления', auto_now=True)


class GoalCategory(DatesModelMixin):
    '''Модель Категории для целей'''
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    title = models.CharField(verbose_name='Название', max_length=255)
    user = models.ForeignKey('core.User', verbose_name='Автор', on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name='Удалена', default=False)


class Goal(DatesModelMixin):
    '''Модель Целей'''
    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'

    class Status(models.IntegerChoices):
        to_do = 1, 'К выполнению'
        in_progress = 2, 'В процессе'
        done = 3, 'Выполнено'
        archived = 4, 'Архив'

    class Priority(models.IntegerChoices):
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
    due_date = models.DateField(verbose_name='Дата выполнения')
    user = models.ForeignKey('core.User', verbose_name='Автор', on_delete=models.PROTECT)
    category = models.ForeignKey(GoalCategory, verbose_name='Категория', related_name='goals', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class GoalComment(DatesModelMixin):
    '''Модель комментариев целей'''
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    goal = models.ForeignKey(Goal,
                             verbose_name='Цель',
                             on_delete=models.PROTECT,
                             related_name='goal_comments')
    user = models.ForeignKey('core.User',
                             verbose_name='Пользователь',
                             on_delete=models.PROTECT,
                             related_name='goal_comments')
    text = models.TextField(verbose_name='Текст комментария')
