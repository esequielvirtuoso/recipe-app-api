from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def create_sample_user(email='test@companydomain.com', password='test1234'):
    """Create a sample user."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful."""
        expected_email = 'test@companydomain.com'
        expected_password = 'TestPass123'
        user = get_user_model().objects.create_user(
            email=expected_email,
            password=expected_password
        )

        self.assertEqual(user.email, expected_email)
        self.assertTrue(user.check_password(expected_password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized."""
        email = 'test@companyDOMAIN.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@companydomain.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation."""
        tag = models.Tag.objects.create(
            user=create_sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)
