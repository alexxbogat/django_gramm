from django.db import models
from cloudinary.models import CloudinaryField


class BaseImage(models.Model):
    file = CloudinaryField('image')
    uploaded_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='%(class)s_images')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AvatarImage(BaseImage):
    pass


class PostImage(BaseImage):
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, related_name='images')
