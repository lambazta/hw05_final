from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.group = Group.objects.create(
            title='Геннадии',
            slug='genas',
            description='This group is only for Genas',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Whats up, dude?',
        )

    def test_post_name_is_text_chars(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostsModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(str(post), expected_object_name)

    def test_group_name_is_title(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostsModelTest.group
        expected_object_name = group.title
        self.assertEqual(str(group), expected_object_name)
