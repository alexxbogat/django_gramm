from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from unittest.mock import patch

from posts.models import Post
from photos.models import AvatarImage, PostImage

User = get_user_model()


class ImageModelsTestCase(TestCase):
    """Tests for the AvatarImage and PostImage models."""

    def setUp(self):
        """Create a test user and post for use in the tests."""
        self.user = User.objects.create_user(username='test_user', password='3C5TeBt21')
        self.post = Post.objects.create(user=self.user, text='Test Test, Test')

    @patch('cloudinary.uploader.upload')
    def test_avatar_image_creation(self, mock_upload):
        """Test creating an AvatarImage with a valid file and user relation."""
        mock_upload.return_value = {
            'public_id': 'test_avatar',
            'version': '1234567890',
            'format': 'jpg',
            'resource_type': 'image',
            'type': 'upload',
            'url': 'https://res.cloudinary.com/demo/image/upload/v1234567890/test_avatar.jpg',
            'secure_url': 'https://res.cloudinary.com/demo/image/upload/v1234567890/test_avatar.jpg',
        }

        avatar_file = SimpleUploadedFile('avatar.jpg', b'avatarcontent', content_type='image/jpeg')
        avatar = AvatarImage.objects.create(file=avatar_file, uploaded_by=self.user)

        self.assertEqual(avatar.uploaded_by, self.user)
        self.assertTrue(avatar.file)
        self.assertIsNotNone(avatar.uploaded_at)

    @patch('cloudinary.uploader.upload')
    def test_post_image_creation(self, mock_upload):
        """Test creating a PostImage with a valid file, related post, and user."""
        mock_upload.return_value = {
            'public_id': 'test_post',
            'version': '1233557799',
            'format': 'jpg',
            'resource_type': 'image',
            'type': 'upload',
            'url': 'https://res.cloudinary.com/demo/image/upload/v1233557799/test_post.jpg',
            'secure_url': 'https://res.cloudinary.com/demo/image/upload/v1233557799/test_post.jpg',
        }
        post_image_file = SimpleUploadedFile('post.jpg', b'postimagecontent', content_type='image/jpeg')
        post_image = PostImage.objects.create(file=post_image_file, uploaded_by=self.user, post=self.post)

        self.assertEqual(post_image.uploaded_by, self.user)
        self.assertEqual(post_image.post, self.post)
        self.assertTrue(post_image.file)
        self.assertIsNotNone(post_image.uploaded_at)
