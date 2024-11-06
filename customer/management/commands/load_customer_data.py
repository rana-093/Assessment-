import json
import sys
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from customer.models import Customer, PurchaseHistory
from restaurant.models import Restaurant, MenuItem


class Command(BaseCommand):
    help = "Load customers data with purchase history."

    def handle(self, *args, **kwargs):
        self.stdout.write("Loading customers data...\n", ending="")

        customer_data = self.load_customer_data('users_with_purchase_history.json')

        for data in customer_data:
            self.process_customer_data(data)

        self.stdout.write(self.style.SUCCESS('Successfully loaded customers data\n'))

    def load_customer_data(self, filename):
        with open(filename, 'r') as file:
            return json.load(file)

    def process_customer_data(self, data):
        customer, created = self.get_or_create_customer(data)
        if not created:
            customer.purchase_history.all().delete()

        for history in data['purchaseHistory']:
            self.process_purchase_history(customer, history)

    def get_or_create_customer(self, data):
        customer, created = Customer.objects.get_or_create(
            name=data['name'],
            customer_id=data['id'],
            defaults={'cash_balance': data['cashBalance']}
        )
        return customer, created

    def process_purchase_history(self, customer, history):
        restaurant = self.get_restaurant_by_name(history['restaurantName'])
        menu = self.get_menu_item_by_name(history['dishName'])

        if not restaurant or not menu:
            raise ValidationError("Restaurant or Menu item does not exist")
        transaction_date = self.convert_to_timezone_aware_datetime(history["transactionDate"])
        self.create_purchase_history(customer, restaurant, menu, transaction_date, history['transactionAmount'])

    def get_restaurant_by_name(self, name):
        return Restaurant.objects.filter(name__iexact=name).first()

    def get_menu_item_by_name(self, name):
        return MenuItem.objects.filter(name__iexact=name).first()

    def convert_to_timezone_aware_datetime(self, transaction_date_str):
        naive_datetime = datetime.strptime(transaction_date_str, "%m/%d/%Y %I:%M %p")
        return timezone.make_aware(naive_datetime, timezone.get_current_timezone())

    def create_purchase_history(self, customer, restaurant, menu, transaction_date, transaction_amount):
        PurchaseHistory.objects.get_or_create(
            customer=customer,
            restaurant=restaurant,
            menu=menu,
            transaction_date=transaction_date,
            defaults={'transaction_amount': transaction_amount}
        )
