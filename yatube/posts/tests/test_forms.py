from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Group, Post, User


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
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.post_author,
            group=cls.group,
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
        self.assertEqual(self.post.author, self.post_author)

    def test_post_edit_form(self):
        """Тест редактирования поста."""
        form_data = {
            'text': 'Измененный пост',
            'group': self.group_2.id,
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
        """Тест, что неавторизованный юзер не может отправить форму
        и перенаправляется на страницу авторизации."""
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
