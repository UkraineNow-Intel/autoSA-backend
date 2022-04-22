import pytest
from django.urls import reverse
from rest_framework import status

from tests.api import factories

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


@pytest.fixture
def tags():
    return [
        factories.TagFactory(name="tag3", slug="slug3"),
        factories.TagFactory(name="tag2", slug="slug2"),
        factories.TagFactory(name="tag1", slug="slug1"),
    ]


def test_list_tags(apiclient, admin_user, tags):
    """Retrieve tags"""
    apiclient.force_authenticate(user=admin_user)

    url = reverse("tag-list")
    response = apiclient.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK
    tags = response.json()["results"]
    assert len(tags) == 3
    tag_names = [t["name"] for t in tags]
    tag_slugs = [t["slug"] for t in tags]
    assert tag_names == ["tag1", "tag2", "tag3"]
    assert tag_slugs == ["slug1", "slug2", "slug3"]
