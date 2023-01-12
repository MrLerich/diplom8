from rest_framework import permissions

from goals.models import BoardParticipant


class BoardPermissions(permissions.BasePermission):
    '''Класс permission для доски'''
    def has_object_permission(self, request, view, obj):
        '''метод должен вернуть True, если доступ у пользователя есть, и
                False  — если нет.
                Если пользователь неавторизован, всегда возвращаем False.
                Если метод запроса входит в SAFE_METHODS (которые не изменяют данные, например GET),
                то тогда просто проверяем, что существует участник у данной доски.
                Если метод не входит (это значит, что мы пытаемся изменить или удалить доску), то обязательно проверяем,
                что наш текущий пользователь является создателем доски.'''
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user, board=obj).exists()
        return BoardParticipant.objects.filter(
            user=request.user, board=obj, role=BoardParticipant.Role.owner
        ).exists()


class GoalCategoryPermissions(permissions.BasePermission):
    '''проверяет авторизацию пользователя и Если метод из списка SAFE_METHODS, то метод проверяет, является ли
    пользователь участником доски.Также метод проверяет, является ли пользователь создателем или участником
    доски с ролью редактор(writer) для редактирования или удаления категории'''
    def has_object_permission(self, request, view, category):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(
                user=request.user,
                board=category.board,
            ).exists()

        return BoardParticipant.objects.filter(
            user=request.user,
            board=category.board,
            role__in=[
                BoardParticipant.Role.owner,
                BoardParticipant.Role.writer,
            ]
        ).exists()


class GoalPermissions(permissions.BasePermission):
    '''проверяет авторизацию пользователя и Если метод из списка SAFE_METHODS, то метод проверяет, является ли
    пользователь участником доски. Также метод проверяет, является ли пользователь создателем или участником доски
    с ролью редактор(writer) для редактирования или удаления цели'''
    def has_object_permission(self, request, view, goal):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return BoardParticipant.objects.filter(user=request.user, board=goal.category.board).exists()
        return BoardParticipant.objects.filter(
            user=request.user,
            board=goal.category.board,
            role__in=[
                BoardParticipant.Role.owner,
                BoardParticipant.Role.writer,
            ]
        ).exists()


class GoalCommentPermissions(permissions.BasePermission):
    '''Метод проверяет авторизацию пользователя и
                что пользователь является создателем комментария'''
    def has_object_permission(self, request, view, comment):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return BoardParticipant.objects.filter(
                user=request.user,
                board=comment.goal.category.board,
                role__in=[
                    BoardParticipant.Role.owner,
                    BoardParticipant.Role.writer,
                ]
            ).exists()
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return comment.user == request.user

