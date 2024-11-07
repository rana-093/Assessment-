from django.urls import path
from restaurant.views import RestaurantOpenView, RestaurantByDishCountView, DishBuyView

urlpatterns = [
    path('v1/restaurants/open', RestaurantOpenView.as_view()),
    path('v1/restaurants/by-dish-count', RestaurantByDishCountView.as_view()),
    path('v1/buy-dish', DishBuyView.as_view()),
]