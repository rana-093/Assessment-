from django.urls import path
from restaurant.views import RestaurantViewSet

urlpatterns = [
    path('v1/login/', LoginView.as_view()),

]