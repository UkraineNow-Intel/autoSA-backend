from rest_framework.test import APIClient
import pytest


@pytest.fixture(scope="session")
def apiclient():
    client = APIClient()
    return client
