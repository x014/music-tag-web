import pytest
from rest_framework.test import APIClient

from applications.user.models import UserProfile


@pytest.mark.django_db
class TestUserProfileModel:
    def test_create_user_profile(self, test_user):
        profile = UserProfile.objects.create(
            user=test_user,
            subsonic_api_token="test-token-123"
        )
        assert profile.user == test_user
        assert profile.subsonic_api_token == "test-token-123"

    def test_user_profile_one_to_one(self, test_user):
        profile = UserProfile.objects.create(user=test_user)
        assert test_user.profile == profile

    def test_subsonic_api_token_blank(self, test_user):
        profile = UserProfile.objects.create(user=test_user)
        assert profile.subsonic_api_token is None or profile.subsonic_api_token == ""


class TestUserViewSets:
    def test_get_user_info(self, authenticated_client):
        response = authenticated_client.get('/user/info/')
        assert response.status_code == 200

    def test_get_user_info_admin(self, admin_client):
        response = admin_client.get('/user/info/')
        assert response.status_code == 200

    def test_get_user_info_normal_user(self, authenticated_client, test_user):
        response = authenticated_client.get('/user/info/')
        assert response.status_code == 200

    def test_get_user_info_unauthenticated(self, api_client):
        response = api_client.get('/user/info/')
        assert response.status_code == 200
