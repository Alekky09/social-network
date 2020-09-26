from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    likes = models.ManyToManyField("Post", blank=True)
    followers = models.ManyToManyField("self", symmetrical=False, blank=True)

    # Returns the users that are followed by our user
    def following(self):
        return User.objects.filter(followers=self)

class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=256, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)