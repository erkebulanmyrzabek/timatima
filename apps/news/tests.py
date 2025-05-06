from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.news.models import News
from apps.accounts.models import User
import uuid
from django.utils import timezone

class NewsModelTest(TestCase):
    """Тесты для модели News"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        self.news = News.objects.create(
            title='Тестовая новость',
            slug='test-news',
            short_description='Краткое описание',
            content='Полный текст новости',
            image='news/images/test.jpg',
            lang='ru',
            is_draft=False,
            published_at=timezone.now(),
            created_by=self.user
        )
    
    def test_news_creation(self):
        """Тест создания новости"""
        self.assertEqual(self.news.title, 'Тестовая новость')
        self.assertEqual(self.news.slug, 'test-news')
        self.assertEqual(self.news.lang, 'ru')
        self.assertEqual(self.news.created_by, self.user)
    
    def test_news_str(self):
        """Тест строкового представления новости"""
        self.assertEqual(str(self.news), 'Тестовая новость')

class NewsAPITest(APITestCase):
    """Тесты для API новостей"""
    
    def setUp(self):
        self.client = APIClient()
        self.news_list_url = reverse('news-list')
        
        # Создаем администратора и обычного пользователя
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        self.user = User.objects.create_user(
            email='user@example.com',
            password='userpass123'
        )
        
        # Создаем тестовую новость
        self.news = News.objects.create(
            title='Тестовая новость',
            slug='test-news',
            short_description='Краткое описание',
            content='Полный текст новости',
            image='news/images/test.jpg',
            lang='ru',
            is_draft=False,
            published_at=timezone.now(),
            created_by=self.admin
        )
        
        # Создаем черновик
        self.draft_news = News.objects.create(
            title='Черновик новости',
            slug='draft-news',
            short_description='Краткое описание черновика',
            content='Полный текст черновика',
            image='news/images/draft.jpg',
            lang='ru',
            is_draft=True,
            published_at=timezone.now(),
            created_by=self.admin
        )
    
    def test_get_news_list_public(self):
        """Тест получения списка новостей для анонимного пользователя"""
        response = self.client.get(self.news_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что в ответе только опубликованные новости (без черновиков)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Тестовая новость')
    
    def test_get_news_list_admin(self):
        """Тест получения списка новостей для администратора"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.news_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем, что администратор видит и черновики
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_news_unauthorized(self):
        """Тест создания новости неавторизованным пользователем"""
        news_data = {
            'title': 'Новая новость',
            'slug': 'new-news',
            'short_description': 'Описание',
            'content': 'Текст',
            'lang': 'ru',
            'is_draft': False,
        }
        response = self.client.post(self.news_list_url, news_data, format='json')
        # Проверяем, что неавторизованные пользователи не могут создавать новости
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_news_regular_user(self):
        """Тест создания новости обычным пользователем"""
        self.client.force_authenticate(user=self.user)
        news_data = {
            'title': 'Новая новость',
            'slug': 'new-news',
            'short_description': 'Описание',
            'content': 'Текст',
            'lang': 'ru',
            'is_draft': False,
        }
        response = self.client.post(self.news_list_url, news_data, format='json')
        # Проверяем, что обычные пользователи не могут создавать новости
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_news_admin(self):
        """Тест создания новости администратором"""
        self.client.force_authenticate(user=self.admin)
        news_data = {
            'title': 'Новая новость от админа',
            'slug': 'new-news-admin',
            'short_description': 'Описание',
            'content': 'Текст',
            'lang': 'ru',
            'is_draft': False,
        }
        response = self.client.post(self.news_list_url, news_data, format='json')
        # Проверяем, что администраторы могут создавать новости
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(News.objects.count(), 3)
