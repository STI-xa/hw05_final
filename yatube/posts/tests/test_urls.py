from django.test import Client, TestCase
from posts.models import Group, Post, User


class PostURLTests(TestCase):
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

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client_non_author = Client()
        self.authorized_client.force_login(PostURLTests.post_author)
        self.user = User.objects.create(
            username='NoName',
        )
        self.authorized_client_non_author.force_login(self.user)
        self.URLS_PUBLIC = {
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.post.author}/',
            'posts/index.html': '/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
        }
        self.POST_CREATE = {
            'posts/create_post.html': '/create/',
        }
        self.POST_EDIT = {
            'posts/create_post.html': f'/posts/{self.post.pk}/edit/',
        }
        self.PRIVATE_URLS = {**self.POST_CREATE, **self.POST_EDIT}
        self.URLS_FOR_ALL = {**self.PRIVATE_URLS, **self.URLS_PUBLIC}

    def test_availability_templates_for_all(self):
        """Проверка доступности шаблонов для всех пользователей"""
        for template, url in self.URLS_FOR_ALL.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location_for_guests(self):
        """Проверка доступности публичных страниц для неавторизованных
        пользователей."""
        for template, url in self.URLS_PUBLIC.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_private_pages_available_for_authorized_users(self):
        """Проверка доступности приватных страниц для авторизованных
        пользователей."""
        for template, url in self.PRIVATE_URLS.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_redirect_private_pages_for_guests(self):
        """Проверка редиректа неавторизованных пользователей для приватных
        страниц."""
        for template, url in self.PRIVATE_URLS.items():
            with self.subTest(url=url):
                response_guests = self.guest_client.get(url)
                self.assertEqual(response_guests.status_code, 302)

    def test_redirect_post_edit_page_for_non_author(self):
        """Проверка редиректа для страницы редактирования поста
        для авторизованного пользователя, но не автора поста."""
        response = self.authorized_client_non_author.get(
            f'/posts/{self.post.pk}/edit/'
        )
        self.assertEqual(response.status_code, 302)

    def test_urls_unexisting_at_desired_location_for_guests(self):
        """Проверка несуществующей страницы для неавторизованных
        пользователей."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
