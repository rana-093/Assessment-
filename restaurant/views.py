from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from datetime import datetime
from restaurant.serializers import RestaurantSerializer, OpeningHourSerializer, MenuItemSerializer
from restaurant.models import Restaurant, OpeningHour, MenuItem

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