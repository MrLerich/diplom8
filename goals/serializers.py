from django.db import transaction
from rest_framework import serializers

from core.models import User
from core.serializers import UserSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


# Board
class BoardCreateSerializer(serializers.ModelSerializer):
    '''создает новую доску'''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        '''мета-класс для указания модели для сериализатора, полей модели сериализатора,
        не изменяемых полей'''
        model = Board
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')
        fields = '__all__'

    def create(self, validated_data):
        '''метод для валидации данных и создания доски'''
        user = validated_data.pop('user')
        board = Board.objects.create(**validated_data)
        BoardParticipant.objects.create(user=user,
                                        board=board,
                                        role=BoardParticipant.Role.owner)
        return board


class BoardParticipantSerializer(serializers.ModelSerializer):
    '''модели сериализатора участников доски'''
    role = serializers.ChoiceField(required=True,
                                   choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field='username',
                                        queryset=User.objects.all())

    class Meta:
        '''Мета-класс для указания модели для сериализатора, полей модели сериализатора,
        и не изменяемых полей'''
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardSerializer(serializers.ModelSerializer):
    '''Класс модели сериализатора доски. просматривает Доски, с возможностью: удаления участников(владельцу себя удалить нельзя); изменения участникам
      уровня доступа(кроме себя - владелец всегда остается владельцем'''
    participants = BoardParticipantSerializer(many=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        '''Мета-класс для указания модели для сериализатора, полей модели сериализатора,
        и не изменяемых полей'''
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated')

    def update(self, instance, validated_data):
        '''для редактирования и добавления участников доски'''
        owner = validated_data.pop('user')
        new_participants = validated_data.pop('participants')
        new_by_id = {part['user'].id: part for part in new_participants}
        old_participants = instance.participants.exclude(user=owner)
        with transaction.atomic():
            for old_participant in old_participants:
                if old_participant.user_id not in new_by_id:
                    old_participant.delete()
                else:
                    if (
                            old_participant.role
                            != new_by_id[old_participant.user_id]['role']
                    ):
                        old_participant.role = new_by_id[old_participant.user_id][
                            'role'
                        ]
                        old_participant.save()
                    new_by_id.pop(old_participant.user_id)
            for new_part in new_by_id.values():
                BoardParticipant.objects.create(
                    board=instance, user=new_part['user'], role=new_part['role']
                )
            instance.title = validated_data['title']
            instance.save()

        return instance


class BoardListSerializer(serializers.ModelSerializer):
    '''для сериализации списка досок'''
    class Meta:
        '''Мета-класс для указания модели для сериализатора, полей модели сериализатора,
        и не изменяемых полей'''
        model = Board
        fields = '__all__'


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    '''создает категорию цели'''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        '''Мета-класс для указания модели для сериализатора, полей модели сериализатора,
        и не изменяемых полей'''
        model = GoalCategory
        read_only_fields = ('id', 'created', 'updated', 'user')
        fields = '__all__'

    def validate_board(self, value):
        '''Метод для валидации данных доски. Метод проверяет не удалена ли доска
                    и является ли пользователь участником с ролью owner или writer'''
        if value.is_deleted:
            raise serializers.ValidationError("not allowed in deleted board")
        if not BoardParticipant.objects.filter(
                board=value,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user=self.context["request"].user,
        ).exists():
            raise serializers.ValidationError("you do not have permission to create goal category in this board")
        return value

class GoalCategorySerializer(serializers.ModelSerializer):
    '''класс модели сериализатора категории целей'''
    user = UserSerializer(read_only=True)

    class Meta:
        '''мета-класс для указания модели для сериализатора, полей модели сериализатора,
        и не изменяемых полей'''
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'board')

    def validated_board(self, value: Board):
        '''Метод для валидации данных доски. Метод проверяет не удалена ли доска
            и является ли пользователь участником с ролью owner или writer'''
        if value.is_deleted:
            raise serializers.ValidationError('Not allowed to delete category')
        if not BoardParticipant.objects.filter(
            board=value,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
            user=self.context['request'].user
        ).exists():
            raise serializers.ValidationError('You must be owner or writer')
        return value

# Goal
class GoalCreateSerializer(serializers.ModelSerializer):
    '''создает цели'''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        '''Мета-класс для указания модели для сериализатора, полей модели сериализатора,
        и не изменяемых полей'''
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    # def validated_category(self, value: GoalCategory):
    #     '''для валидации данных категории целей. Метод проверяет, является ли
    #     пользователь создателем категории, или является ли он участником доски с этой
    #     категорией в роли writer'''
    #     if self.context['request'].user != value.user:
    #         raise PermissionDenied
    #     if not BoardParticipant.objects.filter(
    #         board_is=value.board_id, role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
    #         user=self.context['request'].user,
    #     ).exists():
    #         raise exceptions.PermissionDenied
    #     return value

    def validate_category(self, value):
        if value.is_deleted:
            raise serializers.ValidationError("not allowed in deleted category")

        if not BoardParticipant.objects.filter(
                board_id=value.board_id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user=self.context["request"].user,
        ).exists():
            raise serializers.ValidationError("you do not have permission to create goal in this board")

        return value


class GoalSerializer(serializers.ModelSerializer):
    '''Класс модели сериализатора цели'''
    user = UserSerializer(read_only=True)

    class Meta:
        '''Мета-класс для указания модели для сериализатора, полей модели сериализатора,
        и не изменяемых полей'''
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    # def validate_category(self, value: GoalCategory):
    #     '''для валидации данных категории целей.Метод проверяет, является ли пользователь создателем
    #     категории целей'''
    #     if value.user != self.context['request'].user:
    #         raise serializers.ValidationError('not owner of category')
    #
    #     return value

    def validate_category(self, value):
        '''для валидации данных категории целей.Метод проверяет, является ли пользователь создателем
        категории целей'''
        if value.is_deleted:
            raise serializers.ValidationError("not allowed in deleted category")

        if self.instance.category.board_id != value.board_id:
            raise serializers.ValidationError("this category does not belong to this board")
        return value

# GoalComment
class GoalCommentCreateSerializer(serializers.ModelSerializer):
    '''создает комментарии к цели'''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        '''Мета-класс для указания модели для сериализатора, полей модели сериализатора,
        и не изменяемых полей'''
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')


class GoalCommentSerializer(serializers.ModelSerializer):
    '''класс модели сериализатора комментария'''
    user = UserSerializer(read_only=True)

    class Meta:
        '''Мета-класс для указания модели для сериализатора, полей модели сериализатора,
        и не изменяемых полей'''
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal')
