from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass


class Post(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, related_name = "my_post", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    liked_by = models.ManyToManyField(User)
    liked_post = models.ForeignKey(Post, related_name = "likes", on_delete=models.CASCADE)

class Comment(models.Model):
    content = models.TextField()
    posted_by = models.ForeignKey(User, related_name = "my_comment", on_delete=models.CASCADE)
    linked_comment = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    linked_post = models.ForeignKey(Post, related_name = "comment", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def is_valid_reply(self):
        return self.linked_post == self.linked_comment.linked_post

class Follow(models.Model):
    following = models.ForeignKey(User, related_name = "my_follower", on_delete=models.CASCADE)
    followee = models.ManyToManyField(User)

    





