from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile
from accounts.forms import UserRegistrationForm

class AuthenticationAndProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )

    def test_user_profile_automatically_created(self):
        """Test UserProfile is automatically created via post_save signal."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.display_name, 'Test User')

    def test_user_registration_success(self):
        """Test successful registration with valid details."""
        form_data = {
            'full_name': 'Sarah Connor',
            'username': 'sarahc',
            'email': 'sarah@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        new_user = form.save()
        self.assertEqual(new_user.username, 'sarahc')
        self.assertEqual(new_user.first_name, 'Sarah')
        self.assertEqual(new_user.last_name, 'Connor')
        self.assertTrue(new_user.check_password('SecurePassword123!'))

    def test_registration_duplicate_username_fails(self):
        """Test that registering with duplicate username is prevented."""
        form_data = {
            'full_name': 'Duplicate User',
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_registration_duplicate_email_fails(self):
        """Test that registering with duplicate email is prevented."""
        form_data = {
            'full_name': 'Duplicate Email',
            'username': 'newuser123',
            'email': 'testuser@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_login_and_logout(self):
        """Test login and logout flow."""
        login_success = self.client.login(username='testuser', password='TestPassword123!')
        self.assertTrue(login_success)

        res = self.client.get(reverse('home'))
        self.assertEqual(res.status_code, 200)

        logout_res = self.client.get(reverse('logout'))
        self.assertEqual(logout_res.status_code, 302)

    def test_settings_profile_edit(self):
        """Test profile edit view updates profile fields."""
        self.client.login(username='testuser', password='TestPassword123!')
        res = self.client.post(reverse('settings'), {
            'action': 'edit_profile',
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'New updated bio.',
            'location': 'Tokyo, Japan',
            'website': 'https://updated.dev'
        })
        self.assertEqual(res.status_code, 302)
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.profile.bio, 'New updated bio.')
        self.assertEqual(self.user.profile.location, 'Tokyo, Japan')
