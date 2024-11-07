from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from customer.models import Customer
from restaurant.models import Restaurant


class SearchViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        Customer.objects.create(name="John Doe", cash_balance=1200, customer_id=1)
        Customer.objects.create(name="Johnny Appleseed", cash_balance=1100, customer_id=2)
        Restaurant.objects.create(name="Johnny's Diner", cash_balance=1300)
        Restaurant.objects.create(name="Doe's Eatery", cash_balance=1400)

    def test_no_query_param(self):
        url = reverse('search')
        response = self.client.get(url)
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Please enter a search term')

    def test_no_results_found(self):
        url = reverse('search')
        response = self.client.get(url, {'query': 'Nonexistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_exact_match_results(self):
        url = reverse('search')
        response = self.client.get(url, {'query': 'John Doe'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'John Doe')
        self.assertEqual(results[0]['type'], 'customer')
        self.assertEqual(results[0]['relevance_score'], 6)

    def test_starts_with_and_contains_results(self):
        url = reverse('search')
        response = self.client.get(url, {'query': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data
        self.assertGreater(len(results), 1)
        self.assertEqual(results[0]['relevance_score'], 3)
        self.assertEqual(results[1]['relevance_score'], 3)
        self.assertEqual(results[2]['relevance_score'], 3)
