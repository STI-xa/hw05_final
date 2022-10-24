import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post, User

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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.small_gif_2 = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.uploaded_2 = SimpleUploadedFile(
            name='small.gif_2',
            content=cls.small_gif_2,
            content_type='image/gif',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.post_author,
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.post_author)

    def test_post_create_form(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': self.post.image,
        }
        response_post_create = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_post_create,
                             reverse('posts:profile', args={self.post_author}),
                             )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.group.id, form_data['group'])
        self.assertEqual(self.post.image, form_data['image'])
        self.assertEqual(self.post.author, self.post_author)

    def test_post_edit_form(self):
        """Тест редактирования поста."""
        form_data = {
            'text': 'Измененный пост',
            'group': self.group_2.id,
            self.post.image: self.uploaded_2,
        }
        response_post_edit = self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_post_edit,
                             reverse('posts:post_detail', args={self.post.pk}),
                             )
        self.assertNotEqual(self.post.text, form_data['text'])
        self.assertNotEqual(self.post.group.id, form_data['group'])
        self.assertEqual(self.post.image, self.post.image)
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
