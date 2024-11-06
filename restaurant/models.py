from django.db import models

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=2048)
    cash_balance = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        db_table = 'restaurants'
        indexes = [
            models.Index(fields=['name'])
        ]


class OpeningHour(models.Model):
    DAYS_OF_WEEK = [
        ('Mon', 'Monday'),
        ('Tues', 'Tuesday'),
        ('Weds', 'Wednesday'),
        ('Thurs', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]
    restaurant = models.ForeignKey(Restaurant, related_name="opening_hours", on_delete=models.CASCADE)
    day = models.CharField(max_length=5, choices=DAYS_OF_WEEK)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        db_table = 'restaurant_opening_hours'


class MenuItem(models.Model):
    name = models.CharField(max_length=2048)
    price = models.DecimalField(max_digits=10, decimal_places=4)
    restaurant = models.ForeignKey(Restaurant, related_name="menu_items", on_delete=models.CASCADE)

    class Meta:
        db_table = 'restaurant_menu_items'
        indexes = [
            models.Index(fields=['name'])
        ]
