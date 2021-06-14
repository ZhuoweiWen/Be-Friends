from django.test import TestCase
from django.db import IntegrityError
from .models import *

# Create your tests here.
class Tests(TestCase):

    def setUp(self):
        #Create users
        try:
            Chris = User.objects.create_user(username="Chris", email="", password="test")
            Paul = User.objects.create_user(username="Paul", email="", password="test")
        except IntegrityError:
            pass

        #Create posts
        Post1 = Post.objects.create(content="Good", user = Chris)
        Post2 = Post.objects.create(content="Nice", user = Paul)

    def test_user_link_to_post(self):
        a = Post.objects.get(pk=1)
        self.assertEqual(a.content, "Good")
        self.assertEqual(a.user.username, "Chris")
        


