from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals import serializers
from goals.filters import GoalDateFilter
from goals.models import GoalComment, GoalCategory, Goal



class GoalCategoryCreateView(generics.CreateAPIView):
    '''вьюшка создания категорий'''
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalCategoryCreateSerializer


class GoalCategoryListView(generics.ListAPIView):
    '''вьюшка списка категорий'''
    model = GoalCategory
    permissions_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return GoalCategory.objects.filter(
            user=self.request.user,
            is_deleted=False
        )


class GoalCategoryView(generics.RetrieveUpdateDestroyAPIView):
    '''вьюшка просмотра и удаления категорий'''
    model = GoalCategory
    serializer_class = serializers.GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance


class GoalCreateView(generics.CreateAPIView):
    '''вьюшка создания цели'''
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalCreateSerializer


class GoalListView(generics.ListAPIView):
    '''вьюшка списка целей 12 '''
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter,
                       filters.SearchFilter, ]
    filterset_class = GoalDateFilter
    ordering_fields = ['due_date', 'priority']
    ordering = ['priority', 'due_date']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user).exclude(status=Goal.Status.archived)


class GoalView(generics.RetrieveUpdateDestroyAPIView):
    '''вьюшка просмотра и удаления цели'''
    model = Goal
    serializer_class = serializers.GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.status = Goal.Status.archived  # не удаляем саму сущность
        instance.save()
        return instance


class GoalCommentCreateView(generics.CreateAPIView):
    '''вьюшка создания комментария к цели'''
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalCommentCreateSerializer


class GoalCommentListView(generics.ListAPIView):
    '''вьюшка списка комментариев'''
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.GoalCommentSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.OrderingFilter,
                       filters.SearchFilter]
    ordering_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user)


class GoalCommentView(generics.RetrieveUpdateDestroyAPIView):
    '''вьюшка просмотра комментария'''
    model = GoalComment
    serializer_class = serializers.GoalCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GoalComment.objects.filter(user=self.request.user)
