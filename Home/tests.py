from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AuthenticationTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        self.normal_user = User.objects.create_user(
            username='user',
            password='userpass123',
            email='user@example.com'
        )

    def test_login_page_accessible(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success_admin(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'adminpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_login_success_normal_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'user',
            'password': 'userpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_login_failure_invalid_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_login_failure_empty_fields(self):
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter both username and password')

    def test_login_failure_nonexistent_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_logout_success(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_logout_unauthenticated_user(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_authenticated_user_redirect_from_login(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_login_with_next_parameter(self):
        next_url = '/product/create/'
        response = self.client.get(reverse('login') + f'?next={next_url}')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('login') + f'?next={next_url}', {
            'username': 'admin',
            'password': 'adminpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_url)