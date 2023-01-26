import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_board_create(
    user,
    get_auth_client,
):
    url = reverse('board_create')

    data = {
        'title': 'test board',
    }

    auth_client = get_auth_client(user)

    response = auth_client.post(url, data=data)

    assert response.status_code == 201

    expected_response = {
        'id': response.data['id'],
        'title': 'test board',
        'is_deleted': False,
        'created': response.data['created'],
        'updated': response.data['updated'],
    }

    assert response.data == expected_response
