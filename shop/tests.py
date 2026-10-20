from django.urls import reverse_lazy, reverse
from rest_framework.test import APITestCase

from shop.models import Category, Product


class ShopAPITestCase(APITestCase):
    def format_datetime(self, value):
        # Cette méthode est un helper permettant de formater une date en chaine de caractères sous le même format que
        # celui de l’api
        return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class TestCategory(ShopAPITestCase):
    # Nous stockons l’url de l'endpoint dans un attribut de classe pour pouvoir l’utiliser plus facilement dans
    # chacun de nos tests
    url = reverse_lazy('category-list')

    def test_list(self):
        # Créons deux catégories dont une seule est active
        category = Category.objects.create(name='Fruits', active=True)
        Category.objects.create(name='Légumes', active=False)

        # On réalise l’appel en GET en utilisant le client de la classe de test
        response = self.client.get(self.url)
        # Nous vérifions que le status code est bien 200
        # et que les valeurs retournées sont bien celles attendues
        self.assertEqual(response.status_code, 200)
        excepted = [
            {
                'id': category.pk,
                'name': category.name,
                'date_created': self.format_datetime(category.date_created),
                'date_updated': self.format_datetime(category.date_updated),
            }
        ]
        self.assertEqual(excepted, response.json())

    def test_create(self):
        # Nous vérifions qu’aucune catégorie n'existe avant de tenter d’en créer une
        self.assertFalse(Category.objects.exists())
        response = self.client.post(self.url, data={'name': 'Nouvelle catégorie'})
        # Vérifions que le status code est bien en erreur et nous empêche de créer une catégorie
        self.assertEqual(response.status_code, 405)
        # Enfin, vérifions qu'aucune nouvelle catégorie n’a été créée malgré le status code 405
        self.assertFalse(Category.objects.exists())


class TestProduct(ShopAPITestCase):
    url = reverse_lazy('product-list')

    def test_list(self):
        fruit = Category.objects.create(name='Fruits')
        legume = Category.objects.create(name='Legumes', active=True)

        product_1 = Product.objects.create(name='Orange', active=True, category=fruit)
        product_2 = Product.objects.create(name='Salade', active=True, category=legume)
        Product.objects.create(name='Radis', active=False, category=legume)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        excepted = [
            {
                'id': product_1.pk,
                'name': product_1.name,
                'category': product_1.category_id,
                'date_created': self.format_datetime(product_1.date_created),
                'date_updated': self.format_datetime(product_1.date_updated),
            },
            {
                'id': product_2.pk,
                'name': product_2.name,
                'category': product_2.category_id,
                'date_created': self.format_datetime(product_2.date_created),
                'date_updated': self.format_datetime(product_2.date_updated),
            }
        ]
        self.assertEqual(excepted, response.json())

    def test_list_with_filter(self):
        fruit = Category.objects.create(name='Fruits')
        legume = Category.objects.create(name='Legumes', active=True)

        Product.objects.create(name='Orange', active=True, category=fruit)
        product_2 = Product.objects.create(name='Salade', active=True, category=legume)
        Product.objects.create(name='Radis', active=False, category=legume)

        response = self.client.get(self.url + '?category_id=%i' % legume.id)
        self.assertEqual(response.status_code, 200)
        excepted = [
            {
                'id': product_2.pk,
                'name': product_2.name,
                'category': product_2.category_id,
                'date_created': self.format_datetime(product_2.date_created),
                'date_updated': self.format_datetime(product_2.date_updated),
            }
        ]
        self.assertEqual(excepted, response.json())

    def test_create(self):
        self.assertFalse(Product.objects.exists())
        fruit = Category.objects.create(name='Fruits')

        response = self.client.post(self.url, data={'name': 'Nouveau produit', 'category': fruit.pk})
        self.assertEqual(response.status_code, 405)
        self.assertFalse(Product.objects.exists())
        self.assertEqual(Product.objects.count(), 0)

    def test_delete(self):
        fruit = Category.objects.create(name='Fruits')
        product = Product.objects.create(name='Orange', active=True, category=fruit)
        Product.objects.create(name='Cerise', active=True, category=fruit)

        response = self.client.delete(reverse('product-detail', kwargs={'pk': product.pk}))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Product.objects.count(), 2)
