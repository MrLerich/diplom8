from typing import Type

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def get_auth_client(client):
    def _get_auth_client(user):
        client.force_login(user=user)
        return client

    return _get_auth_client


@pytest.fixture()
def client() -> APIClient:
    return APIClient()
