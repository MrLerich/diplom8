import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_goal_comment_list(user,
                           get_auth_client,
                           board_participant_factory,
                           goal_comment_factory):
    board_participant = board_participant_factory(user=user)
    goal_comments = goal_comment_factory.create_batch(8,
                                                      goal__category__board=board_participant.board,
                                                      goal__category__user=user,
                                                      goal__user=user,
                                                      user=user)
    auth_client = get_auth_client(user)
    url = reverse('goal_comment_list')
    response = auth_client.get(path=url)

    assert response.status_code == 200
    assert len(response.data) == 8
