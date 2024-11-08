from django.urls import path
from customer.views import SearchView, CustomerView, CustomerPurchaseView

urlpatterns = [
    path('v1/search/', SearchView.as_view(), name='search'),
    path('v1/customers', CustomerView.as_view(), name='customers'),
    path('v1/customers/<int:customer_id>/purchase-histories', CustomerPurchaseView.as_view(), name='customers-purchase-view'),
]