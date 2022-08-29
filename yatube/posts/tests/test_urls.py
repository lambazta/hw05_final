from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в БД для проверки доступности
        cls.user = User.objects.create_user(username='tester')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_author = Client()
        self.post_author.force_login(self.post.author)

    # Првоеряем общедоступные страницы
    def test_url_available_to_any_user(self):
        """Общедоступные страницы"""
        pages = [
            '/',
            '/group/test-slug/',
            f'/profile/{self.post.author}/',
            f'/posts/{self.post.id}/',
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_avaliable_to_authorized(self):
        """Авторизованным пользователям"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_available_to_author_post(self):
        """Посты автора"""
        response = self.post_author.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisted_page_to_404(self):
        """Неизвестная страница"""
        response = self.guest_client.get('/unexisted_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_test_uses_correct_template(self):
        """Правильность шаблонов"""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.post.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/unexisted_page/': 'core/404.html',
        }

        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.post_author.get(url)
                self.assertTemplateUsed(response, template)
