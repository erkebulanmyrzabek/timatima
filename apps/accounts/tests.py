from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.accounts.models import User
import uuid

class UserModelTest(TestCase):
    """Тесты для модели User"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123',
            first_name='Иван',
            last_name='Иванов'
        )
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('testpassword123'))
        self.assertEqual(self.user.first_name, 'Иван')
        self.assertEqual(self.user.last_name, 'Иванов')
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.is_active)
    
    def test_user_str(self):
        """Тест строкового представления пользователя"""
        self.assertEqual(str(self.user), 'test@example.com')
    
    def test_get_full_name(self):
        """Тест получения полного имени"""
        self.assertEqual(self.user.get_full_name(), 'Иванов Иван')
        
        # Тест с отчеством
        self.user.middle_name = 'Петрович'
        self.user.save()
        self.assertEqual(self.user.get_full_name(), 'Иванов Иван Петрович')
    
    def test_get_short_name(self):
        """Тест получения короткого имени"""
        self.assertEqual(self.user.get_short_name(), 'Иван')

class AuthAPITest(APITestCase):
    """Тесты для API аутентификации"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'email': 'newuser@example.com',
            'password': 'newuserpass123',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'phone_number': '+7(123)456-78-90'
        }
    
    def test_user_registration(self):
        """Тест регистрации нового пользователя"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'newuser@example.com')
    
    def test_user_login(self):
        """Тест входа пользователя"""
        # Создаем пользователя
        User.objects.create_user(
            email='testlogin@example.com',
            password='testloginpass123'
        )
        
        # Выполняем вход
        response = self.client.post(self.login_url, {
            'email': 'testlogin@example.com',
            'password': 'testloginpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_invalid_login(self):
        """Тест неудачного входа с неверными учетными данными"""
        User.objects.create_user(
            email='testlogin@example.com',
            password='testloginpass123'
        )
        
        # Попытка входа с неверным паролем
        response = self.client.post(self.login_url, {
            'email': 'testlogin@example.com',
            'password': 'wrongpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
