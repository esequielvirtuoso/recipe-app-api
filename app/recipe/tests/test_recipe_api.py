import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    """Return recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_sample_tag(user, name='Main Course'):
    """Create and return a sample tag."""
    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user, name='Cinnamon'):
    """Create and return a sample ingredient."""
    return Ingredient.objects.create(user=user, name=name)


def create_sample_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test uanuthenticated recipe API access."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test anauthenticated recipe API access."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@companydomain.com',
            'test1234'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_sample_recipe(user=self.user)
        create_sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user."""
        second_user = get_user_model().objects.create_user(
            'other@companydomain.com',
            'test1234'
        )
        create_sample_recipe(user=second_user)
        create_sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail."""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        recipe.ingredients.add(create_sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating recipe."""
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags."""
        first_tag = create_sample_tag(user=self.user, name='Vegan')
        second_tag = create_sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [first_tag.id, second_tag.id],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(first_tag, tags)
        self.assertIn(second_tag, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients."""
        first_ingredient = create_sample_ingredient(user=self.user,
                                                    name='Prawns')
        second_ingredient = create_sample_ingredient(user=self.user,
                                                     name='Ginger')
        payload = {
            'title': 'Thai praw red curry',
            'ingredients': [first_ingredient.id, second_ingredient.id],
            'time_minutes': 20,
            'price': 7.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(first_ingredient, ingredients)
        self.assertIn(second_ingredient, ingredients)

    def test_partial_update(self):
        """Test updating a recipe with patch."""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        new_tag = create_sample_tag(user=self.user, name='Curry')

        payload = {'title': 'Chicken tikka', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put."""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        payload = {
            'title': 'Spaghetti carbonra',
            'time_minutes': 25,
            'price': 5.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)

    def test_filter_recipes_by_tags(self):
        """Test returnung recipes with specific tags."""
        first_recipe = create_sample_recipe(user=self.user,
                                            title='Thai vegetable curry')
        second_recipe = create_sample_recipe(user=self.user,
                                             title='Aubergine with tahini')
        first_tag = create_sample_tag(user=self.user, name='Vegan')
        second_tag = create_sample_tag(user=self.user, name='Vegetarian')

        first_recipe.tags.add(first_tag)
        second_recipe.tags.add(second_tag)

        third_recipe = create_sample_recipe(user=self.user,
                                            title='Fish and chips')

        res = self.client.get(
            RECIPES_URL,
            {'tags': f'{first_tag.id},{second_tag.id}'}
        )

        first_serializer = RecipeSerializer(first_recipe)
        second_serializer = RecipeSerializer(second_recipe)
        third_serializer = RecipeSerializer(third_recipe)
        self.assertIn(first_serializer.data, res.data)
        self.assertIn(second_serializer.data, res.data)
        self.assertNotIn(third_serializer.data, res.data)

    def test_filter_recipes_by_ingredients(self):
        """Test returnung recipes with specific ingredients."""
        first_recipe = create_sample_recipe(user=self.user,
                                            title='Posh beans on toast')
        second_recipe = create_sample_recipe(user=self.user,
                                             title='Chicken cacciatore')
        first_ingredient = create_sample_ingredient(user=self.user,
                                                    name='Feta cheese')
        second_ingredient = create_sample_ingredient(user=self.user,
                                                     name='Chicken')

        first_recipe.ingredients.add(first_ingredient)
        second_recipe.ingredients.add(second_ingredient)

        third_recipe = create_sample_recipe(user=self.user,
                                            title='Steak and mushrooms')

        res = self.client.get(
            RECIPES_URL,
            {'ingredients': f'{first_ingredient.id},{second_ingredient.id}'}
        )

        first_serializer = RecipeSerializer(first_recipe)
        second_serializer = RecipeSerializer(second_recipe)
        third_serializer = RecipeSerializer(third_recipe)
        self.assertIn(first_serializer.data, res.data)
        self.assertIn(second_serializer.data, res.data)
        self.assertNotIn(third_serializer.data, res.data)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@companydomain.com',
            'test1234'
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading image to recipe."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'no image'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
