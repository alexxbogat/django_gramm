from urllib.parse import parse_qs, urlparse
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from social_django.models import UserSocialAuth

from photos.models import AvatarImage
from users.models import Profile, Followers

User = get_user_model()


class ModelTestCase(TestCase):
    """Unit tests for the User and Profile models."""

    def setUp(self):
        """Create a test user before each test."""
        self.user = User.objects.create_user(
            username='test_user',
            email='test@test.com',
            password='12345Test'
        )

    def test_user_created(self):
        """Check that the user is created correctly."""
        self.assertEqual(self.user.username, 'test_user')
        self.assertEqual(self.user.email, 'test@test.com')
        self.assertEqual(self.user.id, 1)
        self.assertFalse(self.user.email_verified)

    def test_profile_auto_created(self):
        """Check that the profile is automatically created when a user is created."""
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)

    @patch('cloudinary.uploader.upload')
    def test_profile_fields(self, mock_upload):
        """Check that the profile fields can be updated and saved."""
        mock_upload.return_value = {
            'public_id': 'test_avatar',
            'version': '1234567890',
            'format': 'jpg',
            'resource_type': 'image',
            'type': 'upload',
            'url': 'https://res.cloudinary.com/demo/image/upload/v1234567890/test_avatar.jpg',
            'secure_url': 'https://res.cloudinary.com/demo/image/upload/v1234567890/test_avatar.jpg',
        }
        profile = self.user.profile
        profile.description = 'test_user, test_user'
        avatar_file = SimpleUploadedFile('avatar.jpg', b'avatarcontent', content_type='image/jpeg')
        profile.avatar = AvatarImage.objects.create(file=avatar_file, uploaded_by=self.user)
        profile.save()
        self.assertEqual(profile.description, 'test_user, test_user')
        self.assertIn('test_avatar', profile.avatar.file.public_id)
        self.assertIn('test_avatar', profile.avatar.file.url)


class TestUserView(TestCase):
    """Unit tests for user-related views."""

    def setUp(self):
        """Create a test user and prepare URLs for the tests."""
        self.password = '12345Test'
        self.user = User.objects.create_user(
            username='Test_user',
            email='test@test.com',
            password=self.password,
            is_active=True,
            email_verified=True
        )
        profile = self.user.profile
        profile.save()

        self.client = Client()
        self.url_register = reverse('register')
        self.url_edit_profile = reverse('edit_profile', kwargs={'username': self.user.username})
        self.url_profile = reverse('profile', kwargs={'username': self.user.username})

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_register_and_mail_send(self):
        """Test user registration and verify that an email is sent."""
        data = {
            'username': 'test1',
            'email': 'test1@test.com',
            'password1': '3C5TeBt21',
            'password2': '3C5TeBt21',
        }
        response = self.client.post(self.url_register, data)
        self.assertEqual(len(mail.outbox), 1)
        user = User.objects.get(username='test1')
        user.is_active = True
        user.save()
        logged_in = self.client.login(username='test1', password='3C5TeBt21')
        self.assertTrue(logged_in)

    def test_login_view_success(self):
        """Test successful login for an active user."""
        response = self.client.post(reverse('login'), {
            'username': self.user.username,
            'password': self.password,
        })
        self.assertRedirects(response, reverse('feed'))

    def test_activate_user(self):
        """Test activating a user via the activation link."""
        user = User.objects.create_user(
            username='Test_User',
            email='test_user@test.com',
            password='3C5TeBt21',
            is_active=False
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        response = self.client.get(reverse('activate', args=[uid, token]))
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.email_verified)
        self.assertRedirects(response, reverse('edit_profile', args=[user.username]))

    def test_edit_profile_view_get(self):
        """Test that the edit profile page loads successfully for a logged-in user."""
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('edit_profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)

    def test_subscribe_unsubscribe(self):
        """Test that an authenticated user can subscribe/unsubscribe to another user."""
        self.friend = User.objects.create_user(username='test_user_1', password='3C5TeBt21')
        self.client.login(username='test_user_1', password='3C5TeBt21')
        self.client.post(reverse('subscribe', args=[self.user.id]))
        user_follower = Followers.objects.first()
        self.assertEqual(user_follower.user, self.user)
        self.assertEqual(user_follower.follower, self.friend)

        self.client.post(reverse('subscribe', args=[self.user.id]))
        self.assertFalse(bool(Followers.objects.first()))

    def test_followers_list_view(self):
        """Test that the followers_list view correctly displays users who follow the target user."""
        self.friend = User.objects.create_user(username='test_user_1', password='3C5TeBt21')
        self.client.login(username='test_user_1', password='3C5TeBt21')
        self.client.post(reverse('subscribe', args=[self.user.id]))
        response = self.client.get(reverse('followers_list', args=[self.user.username]))
        followers = response.context['users']
        self.assertIn(self.friend, followers)

    def test_following_list_view(self):
        """Test that the following_list view correctly displays users whom the target user is following."""
        self.friend = User.objects.create_user(username='test_user_1', password='3C5TeBt21')
        self.client.login(username='test_user_1', password='3C5TeBt21')
        self.client.post(reverse('subscribe', args=[self.user.id]))
        response = self.client.get(reverse('following_list', args=[self.friend.username]))
        following = response.context['users']
        self.assertIn(self.user, following)


class OAuthUnittest(TestCase):
    """tests for OAuth login flows (Google and GitHub) using the Django social-auth pipeline."""

    def get_state(self, back: str) -> str:
        """Retrieve the 'state' parameter from the OAuth login redirect."""
        begin_url = reverse('social:begin', args=(back,))
        response = self.client.get(begin_url, follow=False)
        self.assertEqual(response.status_code, 302)

        provider_location = response['Location']
        qs = parse_qs(urlparse(provider_location).query)
        state = qs['state'][0]
        self.assertTrue(state)
        return state

    @patch('social_core.backends.oauth.BaseOAuth2.request_access_token')
    @patch('social_core.backends.google.GoogleOAuth2.user_data')
    def test_google_login_creates_user_and_logs_in(self, mock_user_data, mock_token):
        """Test Google OAuth login flow: user creation, linking, and login session."""
        state = self.get_state('google-oauth2')

        mock_token.return_value = {'access_token': 'fake-token', 'id_token': 'fake-id-token'}

        mock_user_data.return_value = {
            'id': 'google-uid-123',
            'email': 'testovich@test.com',
            'verified_email': True,
            'name': 'Ivan Testovich',
            'given_name': 'Ivan',
            'family_name': 'Testovich'
        }

        response = self.client.get("/auth/complete/google-oauth2/",
                                   {'code': 'dummy-code', 'state': state}, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/feed/')

        user = User.objects.get(email='testovich@test.com')
        self.assertEqual(user.first_name, "Ivan")
        self.assertEqual(user.last_name, "Testovich")

        link = UserSocialAuth.objects.get(user=user, provider='google-oauth2')
        self.assertEqual(link.uid, "testovich@test.com")

        self.assertTrue("_auth_user_id" in self.client.session)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)

    @patch('social_core.backends.oauth.BaseOAuth2.request_access_token')
    @patch('social_core.backends.github.GithubOAuth2.user_data')
    def test_github_login_creates_user_and_logs_in(self, mock_user_data, mock_token):
        """Test GitHub OAuth login flow: user creation, linking, and login session."""
        state = self.get_state('github')

        mock_token.return_value = {'access_token': 'fake-token', 'id_token': 'fake-id-token'}

        mock_user_data.return_value = {
            'id': '123456777',
            'email': 'testovichsasha77@test.com',
            'verified_email': True,
            'name': 'Sasha Testovich'
        }

        response = self.client.get("/auth/complete/github/",
                                   {'code': 'dummy-code', 'state': state}, follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/feed/')

        user = User.objects.get(email='testovichsasha77@test.com')
        self.assertEqual(user.first_name, 'Sasha')
        self.assertEqual(user.last_name, 'Testovich')

        link = UserSocialAuth.objects.get(user=user, provider='github')
        self.assertEqual(link.uid, "123456777")

        self.assertTrue("_auth_user_id" in self.client.session)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.id)
