from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from restaurant.models import Restaurant, MenuItem, OpeningHour

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'

class OpeningHourSerializer(serializers.ModelSerializer):
    restaurant_details = RestaurantSerializer(source='restaurant', read_only=True)
    class Meta:
        model = OpeningHour
        fields = '__all__'