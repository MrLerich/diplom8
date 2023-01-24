import pytest

from goals.models import BoardParticipant


@pytest.mark.django_db
def test_goal_category_list(
        user_factory,
        get_auth_client,
        board_participant_factory,
        goal_category_factory,
):
    user = user_factory()
    board_participant = board_participant_factory(user=user)
    categories = goal_category_factory.create_batch(
        5, board=board_participant.board, user=user
    )

    auth_client = get_auth_client(user)

    response = auth_client.get('/goals/goal_category/list')

    assert response.status_code == 200
    assert len(response.data) == 5


@pytest.mark.django_db
def test_goal_category_list_with_another_auth_user(
        user_factory,
        get_auth_client,
        board_participant_factory,
        goal_category_factory,
):
    user1 = user_factory()
    user2 = user_factory()
    board_participant = board_participant_factory(user=user1)
    categories = goal_category_factory.create_batch(
        5, board=board_participant.board, user=user1
    )

    auth_client = get_auth_client(user2)

    response = auth_client.get('/goals/goal_category/list')

    assert response.status_code == 200
    assert response.data == []
