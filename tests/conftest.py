import pytest
from rest_framework.test import APIClient


@pytest.fixture(scope="session")
def apiclient():
    client = APIClient()
    return client
