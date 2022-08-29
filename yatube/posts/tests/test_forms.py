import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Вася')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='This group is only for tests',
        )
        cls.new_group = Group.objects.create(
            title='New-test-title',
            slug='new_test_slug',
            description='New test description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='This is test text',
            group=cls.group,
        )

        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок
        # и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_author = Client()
        self.post_author.force_login(self.post.author)

    def test_create_post_form(self):
        """Валидная форма создает запись Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test_text',
            'group': f'{self.group.id}',
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': f'{self.user}'}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=form_data['text'],
                group=self.group.id,
                image='posts/small.gif'
            ).exists()
        )
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text=form_data['text'],
                group=self.group.id,
                image='posts/small.gif'
            ).latest('pub_date')
        )

    def test_edit_post_form(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small1.gif',
            content=small_gif,
            content_type='image/gif'
        )
        new_form_data = {
            'text': 'new test text',
            'group': f'{self.new_group.id}',
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.post_author.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'}),
            data=new_form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}))
        # Проверяем, что изменился пост
        self.assertTrue(
            Post.objects.filter(
                text=new_form_data['text'],
                group=f'{self.new_group.id}',
                image='posts/small1.gif',
            ).exists()
        )
