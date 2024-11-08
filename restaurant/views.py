from django.db import transaction
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django.db.models.functions import Lower

from datetime import datetime

from customer.models import Customer, PurchaseHistory
from restaurant.serializers import RestaurantSerializer, OpeningHourSerializer, MenuItemSerializer, DishBuyingSerializer
from restaurant.models import Restaurant, OpeningHour, MenuItem
from customer.serializers import PurchaseHistorySerializer


def alias_python_day_to_db_day(day_name: str):
    day_wise_map = {
        'saturday': 'Sat',
        'sunday': 'Sun',
        'monday': 'Mon',
        'tuesday': 'Tues',
        'wednesday': 'Weds',
        'thursday': 'Thurs',
        'friday': 'Fri',
    }
    return day_wise_map.get(day_name.lower(), day_name)


class RestaurantOpenView(APIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get(self, request):
        datetime_str = request.GET.get('datetime', None)
        if not datetime_str:
            raise ValidationError('Please enter datetime in query params!')
        try:
            formatted_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
            day = formatted_datetime.strftime('%A')
            target_time = formatted_datetime.strftime('%H:%M')
        except:
            raise ValidationError('datetime format should be %Y-%m-%dT%H:%M in 24hrs format')

        opening_hours = OpeningHour.objects.filter(day=alias_python_day_to_db_day(day),
                                                   opening_time__lte=target_time,
                                                   closing_time__gte=target_time)
        restaurants = [op.restaurant for op in opening_hours]
        return Response(RestaurantSerializer(restaurants, many=True).data)


class RestaurantByDishCountView(APIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get(self, request):
        limit = request.GET.get('limit', None)
        dish_count_more_than = request.GET.get('dish_count_more_than', None)
        dish_count_less_than = request.GET.get('dish_count_less_than', None)

        if limit is None and (dish_count_more_than is None and dish_count_less_than is None):
            raise ValidationError(
                "Limit is required, and either dish_count_more_than or dish_count_less_than must be specified.")
        if limit and (dish_count_more_than and dish_count_less_than):
            raise ValidationError("dish_count_more_than or dish_count_less_than must be specified.")

        restaurants_with_dish_counts = Restaurant.objects.annotate(menu_items_count=Count('menu_items'))

        if dish_count_less_than:
            restaurants_with_dish_counts = restaurants_with_dish_counts.filter(
                menu_items_count__lt=int(dish_count_less_than))
        if dish_count_more_than:
            restaurants_with_dish_counts = restaurants_with_dish_counts.filter(
                menu_items_count__gt=int(dish_count_more_than))

        restaurants = restaurants_with_dish_counts.order_by(Lower('name'))[:int(limit)]

        return Response(RestaurantSerializer(restaurants, many=True).data)


class DishBuyView(APIView):
    serializer_class = DishBuyingSerializer

    @transaction.atomic
    def post(self, request):
        serializer = DishBuyingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        menu_id = serializer.validated_data.get('menu_id')
        restaurant_id = serializer.validated_data.get('restaurant_id')
        customer_id = serializer.validated_data.get('customer_id')
        quantity = serializer.validated_data.get('quantity')

        restaurant = Restaurant.objects.select_for_update().get(id=restaurant_id)
        menu_item = MenuItem.objects.get(id=menu_id)
        customer = Customer.objects.get(id=customer_id)

        total_amount = menu_item.price * quantity
        restaurant.cash_balance += total_amount
        customer.cash_balance -= total_amount

        restaurant.save()
        customer.save()

        purchased_transaction = PurchaseHistory.objects.create(restaurant=restaurant,
                                                               menu=menu_item,
                                                               customer=customer,
                                                               transaction_amount=total_amount,
                                                               transaction_date=datetime.now())

        return Response(PurchaseHistorySerializer(purchased_transaction).data, status=status.HTTP_201_CREATED)

class RestaurantView(APIView):
    def get(self, request):
        restaurants = Restaurant.objects.all()
        return Response(data=RestaurantSerializer(restaurants, many=True).data)


class RestaurantDishView(APIView):
    def get(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=int(restaurant_id))
        menus = MenuItem.objects.filter(restaurant=restaurant)
        return Response(data=MenuItemSerializer(menus, many=True).data, status=status.HTTP_200_OK)
