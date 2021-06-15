from django.test import Client, TestCase
from .models import *

import os
import pathlib
import unittest
from selenium import webdriver

driver = webdriver.Chrome('C:/Users/Joey/Documents/chromedriver_win32/chromedriver.exe')

def file_uri(filename):
    return pathlib.Path(os.path.abspath(filename)).as_uri()

# Create your tests here.
class Tests(TestCase):

    def setUp(self):
        #Create users
        
        Chris = User.objects.create_user(username="Chris", email="", password="test")
        Paul = User.objects.create_user(username="Paul", email="", password="test")

        #Create posts
        post1 = Post.objects.create(content="Good", user = Chris)
        post2 = Post.objects.create(content="Nice", user = Paul)

        #Create likes
        like1 = Like.objects.create(liked_post = post1)
        like1.liked_by.add(Chris)

        #Create comments
        comment1 = Comment.objects.create(
            content = "Test comment",
            posted_by = Chris,
            linked_post = post1
        )

        comment2 = Comment.objects.create(
            content = "Re comment1",
            posted_by = Paul,
            linked_comment = comment1,
            linked_post = post2,

        )

        #Create follows

        follow1 = Follow.objects.create(following = Chris)
        follow1.followee.add(Paul)


    def test_post(self):
        a = Post.objects.get(pk=1)
        self.assertEqual(a.content, "Good")
        self.assertEqual(a.user.username, "Chris")

    def test_like(self):
        like1 = Like.objects.get(pk=1)
        post1 = Post.objects.get(pk=1)
        self.assertEqual(post1, like1.liked_post)
        self.assertEqual("Chris", like1.liked_by.all()[0].username)
        
    def test_comment(self):
        comment1 = Comment.objects.get(pk=1)
        comment2 = Comment.objects.get(pk=2)
        post1 = Post.objects.get(pk=1)
        self.assertEqual(post1, comment1.linked_post)
        self.assertFalse(comment1.linked_comment)
        self.assertEqual("Test comment", comment1.content)
        self.assertFalse(comment2.is_valid_reply())

    def test_follow(self):
        follow1 = Follow.objects.get(pk=1)
        Chris = User.objects.get(pk=1)
        self.assertEqual(1, int(follow1.followee.all().count()))
        self.assertEqual(Chris, follow1.following)

    def test_index(self):
        c = Client()
        response = c.get("")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["cur_page"], 1)
        self.assertEqual(response.context["last_page"], 1)
        self.assertTrue(response.context["see_last"])
        self.assertFalse(response.context["following_index"])
        self.assertEqual(len(response.context["posts"]), 2)

    def test_profile(self):
        c = Client()
        response = c.get("/profile/Chris")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["cur_page"], 1)
        self.assertEqual(response.context["last_page"], 1)
        self.assertTrue(response.context["see_last"])
        self.assertEqual(response.context["profile_owner"].username, "Chris")
        self.assertEqual(len(response.context["follower"]), 1)
        self.assertEqual(len(response.context["following"]), 0)
        self.assertEqual(len(response.context["posts"]), 1)
        self.assertFalse(response.context["is_owner"])
        self.assertFalse(response.context["is_following"])


    def test_following_page(self):
        c = Client()
        response = c.post("/login", {'username': 'Paul', 'password': 'test'})
        self.assertEqual(response.status_code, 302)
        response = c.get('/following')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["following_index"])
        self.assertEqual(response.context["user"].username, "Paul")
        self.assertEqual(len(response.context["posts"]), 1)

    def test_follower_page(self):
        c = Client()
        response = c.post("/login", {'username': 'Chris', 'password': 'test'})
        self.assertEqual(response.status_code, 302)
        response = c.get('/follower_page/Chris/follower')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_owner"])
        self.assertEqual(len(response.context["followers"]), 1)
        self.assertEqual(len(response.context["followings"]), 0)
        self.assertEqual(response.context["follow"], "follower")
        self.assertEqual(response.context["profile_owner"].username, "Chris")

class WebpageTests(unittest.TestCase):

    def test_title(self):
        driver.get("C:/Users/Joey/Documents/GitHub/Network/network/templates/network/index.html")
        self.assertEqual(driver.title, "")
