from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    generics,
    permissions
)
from rest_framework.pagination import LimitOffsetPagination

from goals import serializers
from goals.filters import GoalDateFilter
from goals.models import (
    Board,
    Goal,
    GoalCategory,
    GoalComment
)
from goals.permissions import (
    BoardPermissions,
    GoalCategoryPermissions,
    GoalCommentPermissions,
    GoalPermissions
)


# GoalCategory
class GoalCategoryCreateView(generics.CreateAPIView):
    """Вьюшка создания категорий"""
    model = GoalCategory
    serializer_class = serializers.GoalCategoryCreateSerializer
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]


class GoalCategoryListView(generics.ListAPIView):
    """Вьюшка списка категорий к которым у пользователя есть доступ"""
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title', 'board']

    # пользователь должен видеть не только те категории,
    # которые создал сам, но и другие, в досках которых он является участником.
    def get_queryset(self):
        """Метод возвращает из базы queryset списка категорий к которым у пользователя есть доступ"""
        return GoalCategory.objects.filter(board__participants__user=self.request.user,
                                           is_deleted=False)


class GoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    """Вьюшка для отображения, редактирования и удаления категории к которым у пользователя есть доступ"""
    model = GoalCategory
    serializer_class = serializers.GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated, GoalCategoryPermissions]

    def get_queryset(self):
        """Метод возвращает из базы queryset категории к которым у пользователя есть доступ"""
        return GoalCategory.objects.filter(board__participants__user=self.request.user,
                                           is_deleted=False)

    def perform_destroy(self, instance: GoalCategory):
        """Метод удаляет категорию, а у всех целей в этой категории меняет статус на архивный"""
        # with transaction.atomic():
        instance.is_deleted = True
        instance.save()  # update_fields=('is_deleted',)
        # Goal.objects.filter(category=instance).update(status=Goal.Status.archived)
        return instance


# Goals
class GoalCreateView(generics.CreateAPIView):
    """Вьюшка создания цели"""
    model = Goal
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]
    serializer_class = serializers.GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    """Вьюшка списка целей"""
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LimitOffsetPagination
    serializer_class = serializers.GoalSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = GoalDateFilter
    ordering_fields = ['title', 'created']
    ordering = ['title', 'due_date']
    search_fields = ['title', 'description']

    def get_queryset(self):
        """Возвращает из базы queryset списка целей к которым у пользователя есть доступ"""
        return Goal.objects.filter(
            category__board__participants__user=self.request.user
        ).exclude(status=Goal.Status.archived)
        # return Goal.objects.select_related('user', 'category__board').filter(
        #     Q(category__board__participants__user_id=self.request.user.id) & ~Q(status=Goal.Status.archived)
        # )


class GoalView(generics.RetrieveUpdateDestroyAPIView):
    """Вьюшка просмотра, редактирования и удаления цели к которым у пользователя есть доступ"""
    model = Goal
    serializer_class = serializers.GoalSerializer
    permission_classes = [permissions.IsAuthenticated, GoalPermissions]

    def get_queryset(self):
        """Возвращает из базы queryset цели к которому у пользователя есть доступ"""
        return Goal.objects.filter(category__board__participants__user=self.request.user)

    def perform_destroy(self, instance):
        """меняет статус цели как архивный"""
        instance.status = Goal.Status.archived  # не удаляем саму сущность
        instance.save()  # update_fields=('status',)
        return instance


# GoalComment
class GoalCommentCreateView(generics.CreateAPIView):
    """Вьюшка создания комментария к цели"""
    model = GoalComment
    serializer_class = serializers.GoalCommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated, GoalCommentPermissions]


class GoalCommentListView(generics.ListAPIView):
    """Вьюшка списка комментариев"""
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]  # , GoalCommentPermissions
    serializer_class = serializers.GoalCommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter,
                       filters.SearchFilter]
    ordering_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        """Возвращает из базы queryset списка комментариев к которым у пользователя есть доступ"""
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


class GoalCommentView(generics.RetrieveUpdateDestroyAPIView):
    """Вьюшка просмотра, редактирования и удаления комментария к которым у пользователя есть доступ"""
    model = GoalComment
    serializer_class = serializers.GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated, GoalCommentPermissions]

    def get_queryset(self):
        """Возвращает из базы queryset комментария к которому у пользователя есть доступ"""
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)


# Board
class BoardCreateView(generics.CreateAPIView):
    """Вьюшка создания доски"""
    model = Board
    permissions = [permissions.IsAuthenticated]
    serializer_class = serializers.BoardCreateSerializer


class BoardView(generics.RetrieveUpdateDestroyAPIView):
    """Вьюшка просмотра, редактирования и удаления доски к которой у пользователя есть доступ"""
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = serializers.BoardSerializer

    def get_queryset(self):
        """Возвращает из базы queryset доски к которой у пользователя есть доступ"""
        # Обратите внимание на фильтрацию – она идет через participants
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance: Board):
        """Удаляет доску, и все категории и цели в ней"""
        # При удалении доски помечаем ее как is_deleted, «удаляем» категории,
        # обновляем статус целей
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()  # update_fields=['is_deleted']
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
        return instance


class BoardListView(generics.ListAPIView):
    """Вьюшка просмотра списков досок к которым у пользователя есть доступ"""
    model = Board
    permission_classes = [permissions.IsAuthenticated, BoardPermissions]
    serializer_class = serializers.BoardListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self):
        """Возвращает из базы queryset списка досок к которым у пользователя есть доступ"""
        return Board.objects.filter(participants__user=self.request.user, is_deleted=False)
