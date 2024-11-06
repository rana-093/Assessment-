from django.urls import path
from restaurant.views import RestaurantOpenView

urlpatterns = [
    path('v1/restaurants/open', RestaurantOpenView.as_view()),
]