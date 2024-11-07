from django.urls import path
from customer.views import SearchView

urlpatterns = [
    path('v1/search/', SearchView.as_view(), name='search'),
]