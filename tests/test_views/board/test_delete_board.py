import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_board_delete(
        get_auth_client,
        board_participant,
):
    auth_client = get_auth_client(board_participant.user)
    url = reverse('board_detail', kwargs={'pk': board_participant.pk})
    response = auth_client.delete(path=url)

    assert response.status_code == 204
    assert response.data is None


@pytest.mark.django_db
def test_board_delete_with_another_auth_user(
        user_factory,
        get_auth_client,
        board_participant,
):
    user2 = user_factory()

    auth_client = get_auth_client(user2)

    url = reverse('board_detail', kwargs={'pk': board_participant.pk})
    response = auth_client.delete(path=url)

    assert response.status_code == 404
    assert response.data == {'detail': 'Not found.'}
