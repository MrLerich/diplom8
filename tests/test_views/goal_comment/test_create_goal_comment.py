import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_goal_comment_create(
    user,
    get_auth_client,
    board_participant_factory,
    goal_factory,
):
    board_participant = board_participant_factory(user=user)
    goal = goal_factory(user=user, category__board=board_participant.board)

    data = {
        'goal': goal.id,
        'text': 'test comment',
    }

    auth_client = get_auth_client(user)
    url = reverse('goal_comment_create')
    response = auth_client.post(
        path=url,
        data=data,
    )

    assert response.status_code == 201

    expected_response = {
        'id': response.data['id'],
        'text': 'test comment',
        'goal': goal.id,
        'created': response.data['created'],
        'updated': response.data['updated'],
    }

    assert response.data == expected_response


@pytest.mark.django_db
def test_goal_comment_create_with_not_auth_user(
    user,
    get_auth_client,
    board_participant_factory,
    goal_factory,
    client,
):
    board_participant = board_participant_factory(user=user)
    goal = goal_factory(user=user, category__board=board_participant.board)

    data = {
        'goal': goal.id,
        'text': 'test comment',
    }
    url = reverse('goal_comment_create')
    response = client.post(path=url, data=data)

    assert response.status_code == 403
    assert response.data == {
        'detail': 'Authentication credentials were not provided.'
    }
