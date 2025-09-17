from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from unittest.mock import patch

from posts.models import Post, Like, Tag
from photos.models import PostImage

User = get_user_model()


class CloudinaryMockMixin:
    """Mixin for mocking Cloudinary image uploads"""

    mock_upload_return_value = {
        'public_id': 'test_post',
        'version': '1233557799',
        'format': 'jpg',
        'resource_type': 'image',
        'type': 'upload',
        'url': 'https://res.cloudinary.com/demo/image/upload/v1233557799/test_post.jpg',
        'secure_url': 'https://res.cloudinary.com/demo/image/upload/v1233557799/test_post.jpg',
    }

    def mock_cloudinary(self, mock_upload):
        mock_upload.return_value = self.mock_upload_return_value


class ModelTestCase(TestCase, CloudinaryMockMixin):
    """Tests for Post-related models"""

    def setUp(self):
        """Create a test user for related models."""
        self.user = User.objects.create_user(
            username='test_user',
            email='test@test.com',
            password='12345Test'
        )

    def test_tag_creation(self):
        """Test that a Tag instance can be created correctly."""
        tag = Tag.objects.create(name='test')
        self.assertEqual(tag.name, 'test')

    def test_post_creation_and_fields(self):
        """Test creation of a Post and its fields are saved properly."""
        post = Post.objects.create(user=self.user, text='Test User')
        self.assertEqual(post.text, 'Test User')
        self.assertEqual(post.user, self.user)
        self.assertIsNotNone(post.created_at)

    def test_post_tag_relationship(self):
        """Test that tags can be associated with a post."""
        tag = Tag.objects.create(name='test')
        post = Post.objects.create(user=self.user, text='Test User')
        post.tags.add(tag)
        self.assertIn(tag, post.tags.all())

    @patch('cloudinary.uploader.upload')
    def test_post_image_creation(self, mock_upload):
        """Test creation of a PostImage associated with a post."""
        self.mock_cloudinary(mock_upload)
        post_image_file = SimpleUploadedFile('post.jpg', b'postimagecontent', content_type='image/jpeg')
        post = Post.objects.create(user=self.user, text='Test User')
        image = PostImage.objects.create(post=post, file=post_image_file, uploaded_by=self.user)
        self.assertEqual(image.post, post)
        self.assertEqual(image.uploaded_by, self.user)
        self.assertTrue(bool(image.file))

    def test_like_creat_del(self):
        """Test that a Like can be created and is deleted upon post deletion."""
        post = Post.objects.create(user=self.user, text='Test User')
        like = Like.objects.create(user=self.user, post=post)
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.post, post)
        post.delete()
        self.assertFalse(Like.objects.filter(id=like.id).exists())


class PostViewsTest(TestCase, CloudinaryMockMixin):
    """Tests for views related to posts"""

    def setUp(self):
        """Set up test client and authenticated test user."""
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', password='3C5TeBt21')
        self.client.login(username='test_user', password='3C5TeBt21')

    def test_create_post_view_get(self):
        """GET request to create_post should render the form."""
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    @patch('cloudinary.uploader.upload')
    def test_create_post_view_post(self, mock_upload):
        """POST request to create_post should create post and redirect to feed."""
        self.mock_cloudinary(mock_upload)
        post_image_file = SimpleUploadedFile('post.jpg', b'postimagecontent', content_type='image/jpeg')
        data = {
            'text': 'Test, ttttest!',
            'tags': 'django, test, task',
            'images': [post_image_file]
        }
        response = self.client.post(reverse('create_post'), data, format='multipart')
        post = Post.objects.first()
        self.assertEqual(post.text, 'Test, ttttest!')
        self.assertEqual(post.tags.count(), 3)
        self.assertEqual(PostImage.objects.count(), 1)
        self.assertRedirects(response, reverse('feed'))

    @patch('cloudinary.uploader.upload')
    def test_delete_post_view_post(self, mock_upload):
        """Test that POST request to delete_post removes the post and associated images."""
        self.mock_cloudinary(mock_upload)
        post_image_file = SimpleUploadedFile('post.jpg', b'postimagecontent', content_type='image/jpeg')
        data = {
            'text': 'Test, ttttest!',
            'tags': 'django, test, task',
            'images': [post_image_file]
        }
        self.client.post(reverse('create_post'), data, format='multipart')
        post = Post.objects.first()
        self.client.post(reverse('delete_post', args=[post.id]), HTTP_REFERER=reverse('feed'))
        self.assertFalse(Post.objects.filter(id=post.id).exists())
        self.assertEqual(PostImage.objects.count(), 0)

    @patch('cloudinary.uploader.upload')
    def test_edit_post_view_post(self, mock_upload):
        """Test that POST request to edit_post updates the post text, tags, and adds new images."""
        self.mock_cloudinary(mock_upload)
        image_1 = SimpleUploadedFile("test_1.jpg", b"file_content", content_type="image/jpeg")
        image_2 = SimpleUploadedFile("test_2.jpg", b"file_content", content_type="image/jpeg")
        data_1 = {
            'text': 'Test, post test edit!',
            'tags': 'nice, test, summer',
            'images': [image_1]
        }
        data_2 = {
            'text': 'Test, edit!',
            'tags': 'work, nice',
            'images': [image_2]
        }
        self.client.post(reverse('create_post'), data_1, format='multipart')
        post = Post.objects.first()

        self.client.post(reverse('edit_post', args=[post.id]),
                         data_2, format='multipart',
                         HTTP_REFERER=reverse('feed'))
        post = Post.objects.first()
        self.assertEqual(post.text, 'Test, edit!')
        self.assertEqual(post.tags.count(), 2)
        self.assertEqual(PostImage.objects.count(), 2)

    def test_like_view_toggle(self):
        """Should like and unlike a post."""
        post = Post.objects.create(user=self.user, text='Likeable post')

        response = self.client.post(reverse('like', args=[post.id]))
        self.assertEqual(response.json()['liked'], True)
        self.assertEqual(response.json()['likes_count'], 1)

        response = self.client.post(reverse('like', args=[post.id]))
        self.assertEqual(response.json()['liked'], False)
        self.assertEqual(response.json()['likes_count'], 0)

    def test_feed_view(self):
        """Feed view should return a list of posts with prefetch data."""
        Post.objects.create(user=self.user, text='test 1')
        Post.objects.create(user=self.user, text='test 2')
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/feed.html')
        self.assertContains(response, 'test 1')
        self.assertContains(response, 'test 2')

    def test_friends_news_view(self):
        """Tests the friends_news view for an authenticated user."""
        Post.objects.create(user=self.user, text='test 1')
        Post.objects.create(user=self.user, text='test 2')

        self.friend = User.objects.create_user(username='test_user_1', password='3C5TeBt21')
        self.client.login(username='test_user_1', password='3C5TeBt21')
        self.client.post(reverse('subscribe', args=[self.user.id]))

        response = self.client.get(reverse('friends_news'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'posts/friends_news.html')
        self.assertContains(response, 'test 1')
        self.assertContains(response, 'test 2')
