from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='tester')
        cls.user_2 = User.objects.create_user(username='test-author')
        cls.user_3 = User.objects.create_user(username='tester-2')
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
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Comment text',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_author = Client()
        self.post_author.force_login(self.post.author)

    def test_views_uses_correct_template(self):
        """View-функции используют соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': f'{self.group.slug}'}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user}'}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}): (
                    'posts/post_detail.html'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'}): (
                    'posts/create_post.html'),
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка словаря контекста главной страницы (в нём передаётся форма)
    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        # Проверяем, что типы полей формы в словаре context соответствуют
        # ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.post_author.get(reverse(
            'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        # Проверяем, что типы полей формы в словаре context соответствуют
        # ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse(
            'posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, f'{self.post.text}')
        self.assertEqual(post_group_0, f'{self.post.group}')
        self.assertEqual(post_image_0, f'{self.post.image}')

    # Проверяем, что словарь context страницы /group/test-slug
    # в первом элементе списка post_list содержит ожидаемые значения
    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, f'{self.post.text}')
        self.assertEqual(post_group_0, f'{self.post.group}')
        self.assertEqual(post_image_0, f'{self.post.image}')

    def test_profile_page_show_correct_context(self):
        """Шаблон prifile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': f'{self.user}'}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, f'{self.post.text}')
        self.assertEqual(post_group_0, f'{self.post.group}')
        self.assertEqual(post_image_0, f'{self.post.image}')

    # Проверяем, что словарь context страницы posts/post_id
    # содержит ожидаемые значения
    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': f'{self.post.id}'})))
        self.assertEqual(
            response.context.get(
                'post').author.username, f'{self.post.author}')
        self.assertEqual(
            response.context.get('post').text, f'{self.post.text}')
        self.assertEqual(
            response.context.get('post').group.title, f'{self.post.group}')
        self.assertEqual(
            response.context.get('post').image, f'{self.post.image}')

    def test_post_not_exist_in_another_group_list(self):
        """Пост не попал в группу, для которой не был предназначен."""
        group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test1-slug',
            description='Тестовое описание 1',
        )
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': f'{group1.slug}'}))
        self.assertFalse(response.context['page_obj'])

    def test_guest_client_can_not_add_comment(self):
        """Неавторизованный пользователь не может оставлять комментарии"""
        response = self.guest_client.get(
            reverse(
                'posts:add_comment', kwargs={'post_id': f'{self.post.id}'}))
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/')

    def test_comment_exists_on_post_detail_page(self):
        """Комментарий отображается на странице поста"""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}))
        self.assertContains(response, self.comment.text)

    def test_index_page_caching(self):
        """Главная страница кэшируется """
        response = self.guest_client.get(reverse('posts:index'))
        test_post = Post.objects.get(id=self.post.id)
        test_post.delete()
        response_cached = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_cached.content)
        cache.clear()
        response_cleared = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(response_cached.content, response_cleared.content)

    def test_authorized_client_can_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей и удалять их из подписок."""
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': f'{self.user_2}'}
        ))
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.user_2
            ).exists())
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': f'{self.user_2}'}
        ))
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.user_2
            ).exists())

    def test_new_post_is_in_follower_feed(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': f'{self.user_2}'}
        ))
        authorized_client_2 = Client()
        authorized_client_2.force_login(self.user_2)
        authorized_client_2.post(reverse(
            'posts:post_create'), data={'text': 'Тестовый текст 2'})
        follower_response = self.authorized_client.get(
            reverse(
                'posts:follow_index'))
        authorized_client_3 = Client()
        authorized_client_3.force_login(self.user_3)
        response = authorized_client_3.get(
            reverse(
                'posts:follow_index'))
        self.assertContains(follower_response, 'Тестовый текст 2')
        self.assertNotContains(response, 'Тестовый текст 2')
