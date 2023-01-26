import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_goal_create(
    user,
    get_auth_client,
    board_participant_factory,
    goal_category_factory,
):
    board_participant = board_participant_factory(user=user)
    category = goal_category_factory(board=board_participant.board, user=user)

    data = {
        'category': category.pk,
        'title': 'test goal',
        'description': 'description'
    }

    auth_client = get_auth_client(user)
    url = reverse('goal_create')
    response = auth_client.post(
        path=url,
        data=data,
    )

    assert response.status_code == 201

    expected_response = {
        'id': response.data['id'],
        'title': 'test goal',
        'category': category.id,
        'description': 'description',
        'due_date': None,
        'status': 1,
        'priority': 2,
        'created': response.data['created'],
        'updated': response.data['updated'],
    }

    assert response.data == expected_response
