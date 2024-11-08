from django.urls import path
from restaurant.views import RestaurantOpenView, RestaurantByDishCountView, DishBuyView, RestaurantDishView, RestaurantView

urlpatterns = [
    path('v1/restaurants/open', RestaurantOpenView.as_view()),
    path('v1/restaurants/by-dish-count', RestaurantByDishCountView.as_view()),
    path('v1/buy-dish', DishBuyView.as_view()),
    path('v1/restaurants/<int:restaurant_id>/menus', RestaurantDishView.as_view(), name='restaurant-dishes'),
    path('v1/restaurants', RestaurantView.as_view(), name='restaurants'),
]