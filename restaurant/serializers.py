from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from customer.models import Customer
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


class DishBuyingSerializer(serializers.Serializer):
    dish_id = serializers.IntegerField(write_only=True)
    restaurant_id = serializers.IntegerField(write_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
        validated_data = super(DishBuyingSerializer, self).validate(attrs)
        dish_id = validated_data['dish_id']
        restaurant_id = validated_data['restaurant_id']
        customer_id = validated_data['customer_id']

        restaurant = Restaurant.objects.filter(id=restaurant_id)
        if not restaurant.exists():
            raise ValidationError('Restaurant not found')
        restaurant = restaurant.first()

        menu = MenuItem.objects.filter(id=dish_id, restaurant=restaurant)
        if not menu.exists():
            raise ValidationError('Dish not found in this restaurant')
        menu = menu.first()

        customer = Customer.objects.filter(id=customer_id)
        if not customer.exists():
            raise ValidationError('Customer not found')
        customer = customer.first()

        validated_data['menu'] = menu
        validated_data['restaurant'] = restaurant
        validated_data['customer'] = customer
        validated_data['menu_id'] = dish_id
        validated_data['customer_id'] = customer_id
        return validated_data