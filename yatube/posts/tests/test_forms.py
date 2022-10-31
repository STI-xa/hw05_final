import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create(
            username='post_author',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )
        cls.comment = Comment.objects.create(
            author=cls.post_author,
            text='Тестовый комментарий',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.post_author,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=False)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_post_create_form(self):
        """Валидная форма создает запись в Post."""
        small_gif_1 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_1 = SimpleUploadedFile(
            name='small.gif_1',
            content=small_gif_1,
            content_type='image/gif',
        )
        post = Post.objects.create(
            text='Тестовый текст',
            author=self.post_author,
            group=self.group,
            image=uploaded_1
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': post.image.name,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image.name, form_data['image'])
        self.assertEqual(post.author, self.post_author)

    def test_post_edit_form(self):
        """Тест редактирования поста."""
        form_data = {
            'text': 'Измененный пост',
            'group': self.group_2.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(self.post.text, form_data['text'])
        self.assertNotEqual(self.post.group.id, form_data['group'])
        self.assertEqual(self.post.author, self.post_author)

    def test_post_create_form_for_guests(self):
        """Тест, что неавторизованный юзер не может отправить форму и
        и перенаправляется на страницу авторизации."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response_post_create_guest = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_post_create_guest,
                             ('/auth/login/?next='
                              + reverse('posts:post_create')),
                             )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_comment_form_for_auth_users(self):
        """Тест создания комментов авторизованным пользователем."""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Тестовый коммент'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={
                              'post_id': self.post.id}),
        )
        self.assertEqual(self.comment.author, self.post_author)
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_comment_form_for_guests(self):
        """Тест, что неавторизованный юзер не может оставить коммент."""
        comments_count = Comment.objects.count()
        form_data = {'text': 'Тестовый коммент'}
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response,
                             ('/auth/login/?next='
                              + reverse('posts:add_comment',
                                        kwargs={'post_id': self.post.id})
                              ),
                             )
        self.assertEqual(Post.objects.count(), comments_count)
