from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.posts = [
            Post(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            ) for i in range(1, 14)
        ]
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка index: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        # Проверка index: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse(
                'posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        # Проверка: количество постов на первой странице группы равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_second_page_contains_three_records(self):
        # Проверка: на второй странице группы должно быть три поста.
        response = self.client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': f'{self.group.slug}'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{self.user}'}))
        # Проверка: количество постов на первой странице профиля равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        # Проверка: на второй странице профиля должно быть три поста.
        response = self.client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': f'{self.user}'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
