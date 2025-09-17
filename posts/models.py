from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="posts")
    text = models.TextField()
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user.username} on {self.created_at}"


class Like(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"#{self.name}"
