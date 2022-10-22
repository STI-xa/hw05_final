import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User


class PostViewsTests(TestCase):
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
        cls.urls_and_namespaces = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_list', kwargs={'slug': cls.group.slug}),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': cls.post_author}),
            'posts/post_detail.html':
                reverse('posts:post_detail', args={cls.post.id}),
            'posts/create_post.html':
                reverse('posts:post_edit', args={cls.post.id}),
        }
        cls.post_create_page = {
            'posts/create_post.html': reverse('posts:post_create'),
        }
        cls.urls_for_all = {**cls.urls_and_namespaces, **cls.post_create_page}

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTests.post_author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.urls_for_all.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def _assert_post_has_equal_context(self, post):
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author, self.post.author)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page_obj')), 1)
        check_value = response.context.get('page_obj')[0]
        self._assert_post_has_equal_context(check_value)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'})
        )
        self.assertEqual(len(response.context.get('page_obj')), 1)
        check_value = response.context.get('page_obj')[0]
        check_group = response.context.get('group')
        self._assert_post_has_equal_context(check_value)
        self.assertEqual(check_group, self.group)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args={self.post.id})
        )
        check_value = response.context.get('post')
        self._assert_post_has_equal_context(check_value)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args={self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = (
                    response.context.get('form').fields.get(value)
                )
                self.assertIsInstance(form_field, expected)
                self.assertEqual(response.context['is_edit'], True)

    def test_post_profile_page_show_correct_context(self):
        """Шаблон post_profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.post_author})
        )
        self.assertEqual(len(response.context.get('page_obj')), 1)
        check_value = response.context.get('page_obj')[0]
        check_author = response.context.get('author')
        self._assert_post_has_equal_context(check_value)
        self.assertEqual(check_author, self.post_author)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = (
                    response.context.get('form').fields.get(value)
                )
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        """Проверка добавления поста на указанных страницах."""
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': 'post_author'}))
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(self.post, index,
                      'Ошибка проверки поста на главной странице')
        self.assertIn(self.post, group,
                      'Ошибка проверки поста на странице группы')
        self.assertIn(self.post, profile,
                      'Ошибка проверки поста на странице профайла')

    def test_post_added_correctly_in_group(self):
        """Проверка ошибочного добавления поста в другую группу"""
        group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание2',
        )
        response_group_2 = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test_slug_2'}))
        group_2 = response_group_2.context['page_obj']
        self.assertNotIn(self.post, group_2,
                         'Ошибка теста поста, который не должен попасть'
                         'в другую группу'
                         )

    def test_cache_index_page(self):
        """Проверка кеша."""
        response = self.guest_client.get(reverse('posts:index'))
        old_response = response.content
        Post.objects.get(id=1).delete()
        response_new = self.guest_client.get(reverse('posts:index'))
        new_response = response_new.content
        self.assertEqual(old_response, new_response)

    def test_follow_page(self):
        """Тест авторизованный пользователь может подписываться на других
        пользователей."""
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
        Follow.objects.get_or_create(
            user=self.post_author, author=self.post.author)
        response_follower = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(len(response_follower.context['page_obj']), 1)
        self.assertIn(self.post, response_follower.context['page_obj'])

        """Проверка что пост не появился у того, кто не подписан"""
        another_user = User.objects.create(username="NoName")
        self.authorized_client.force_login(another_user)
        response_another_follower = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertNotIn(
            self.post, response_another_follower.context['page_obj'])

        """Проверка отмены отписки"""
        Follow.objects.all().delete()
        response_for_delete = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(len(response_for_delete.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    NUMBER_POSTS_FOR_PAGINATOR_TEST = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create(
            username='post_author_2',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create(
            [Post(
                text=f'Тестовый текст{i}',
                author=cls.post_author,
                group=cls.group)
                for i in range(cls.NUMBER_POSTS_FOR_PAGINATOR_TEST)
             ]
        )

    def setUp(self):
        self.client = Client()
        self.authorized_client = Client()
        self.user = PaginatorViewsTest.post_author
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        pages = [
            reverse('posts:index'),
            reverse(
                'posts:profile', kwargs={'username': self.user}),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
        ]
        for page in pages:
            respons_first_page = self.client.get(page)
            respons_second_page = self.client.get(page + '?page=2')
        self.assertEqual(
            len(respons_first_page.context['page_obj']),
            settings.NUM_POSTS_ON_PAGE
        )
        self.assertEqual(len(respons_second_page.context['page_obj']),
                         (self.NUMBER_POSTS_FOR_PAGINATOR_TEST
                         - settings.NUM_POSTS_ON_PAGE)
                         )


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_image_in_index_profile_and_group_list_pages(self):
        """Картинка передается на страницы index, profile и group_list."""
        urls = (
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.post.author}),
        )
        for url in urls:
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context.get('page_obj')), 1)
                check_value = response.context['page_obj'][0]
                self.assertEqual(check_value.image, self.post.image)

    def test_image_in_post_detail_page(self):
        """Картинка передается на страницу post_detail."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        check_value = response.context['post']
        self.assertEqual(check_value.image, self.post.image)

    def test_image_in_db(self):
        """Проверяем что пост с картинкой создается в БД."""
        self.assertTrue(
            Post.objects.filter(text='Тестовый текст',
                                image='posts/small.gif').exists(),
        )
