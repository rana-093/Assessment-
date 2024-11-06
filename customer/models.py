from django.db import models
from restaurant.models import Restaurant, MenuItem

class Customer(models.Model):
    name = models.CharField(max_length=512)
    customer_id = models.IntegerField()
    cash_balance = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        db_table = 'customers'
        indexes = [
            models.Index(fields=['name'])
        ]

class PurchaseHistory(models.Model):
    customer = models.ForeignKey(Customer, related_name='purchase_history', on_delete=models.CASCADE)
    menu = models.ForeignKey(MenuItem, related_name='purchase_history', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, related_name='purchase_history', on_delete=models.CASCADE)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=4)
    transaction_date = models.DateTimeField()

    class Meta:
        db_table = 'purchase_histories'
        indexes = [
            models.Index(fields=['customer', 'menu', 'restaurant'])
        ]