import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_goal_update(
    user,
    get_auth_client,
    board_participant_factory,
    goal_factory,
):
    board_participant = board_participant_factory(user=user)
    goal = goal_factory(
        category__board=board_participant.board, category__user=user, user=user
    )

    data = {
        'title': 'test goal!',
    }

    auth_client = get_auth_client(user)
    url = reverse('goal_detail', kwargs={'pk': goal.pk})
    response = auth_client.patch(
        path=url,
        data=data,
    )

    expected_response = {
        'id': goal.id,
        'title': 'test goal!',
        'category': goal.category.id,
        'description': '',
        'due_date': None,
        'status': 1,
        'priority': 2,
        'created': goal.created.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        'updated': response.data['updated'],
        'user': {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        },
    }

    assert response.status_code == 200
    assert response.data == expected_response
