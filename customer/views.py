from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Case, When, IntegerField, Value, F, CharField
from django.db.models.functions import Lower
from customer.models import Customer
from restaurant.models import Restaurant

class SearchView(APIView):
    def get(self, request):
        search = request.GET.get('search')
        if not search:
            raise ValidationError('Please enter a search term')

        customer_results = Customer.objects.annotate(
            type=Value('customer', output_field=CharField()),
            exact_match=Case(
                When(name__iexact=search, then=Value(3)),
                default=Value(0),
                output_field=IntegerField()
            ),
            starts_with_match=Case(
                When(name__istartswith=search, then=Value(2)),
                default=Value(0),
                output_field=IntegerField()
            ),
            contains_match=Case(
                When(name__icontains=search, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).annotate(
            relevance_score=F('exact_match') + F('starts_with_match') + F('contains_match')
        ).exclude(relevance_score=0).values('name', 'type', 'relevance_score')

        restaurant_results = Restaurant.objects.annotate(
            type=Value('restaurant', output_field=CharField()),
            exact_match=Case(
                When(name__iexact=search, then=Value(3)),
                default=Value(0),
                output_field=IntegerField()
            ),
            starts_with_match=Case(
                When(name__istartswith=search, then=Value(2)),
                default=Value(0),
                output_field=IntegerField()
            ),
            contains_match=Case(
                When(name__icontains=search, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).annotate(
            relevance_score=F('exact_match') + F('starts_with_match') + F('contains_match')
        ).exclude(relevance_score=0).values('name', 'type', 'relevance_score')
        combined_results = customer_results.union(restaurant_results)
        sorted_results = combined_results.order_by('-relevance_score')

        results = []
        for result in sorted_results:
            results.append({
                'type': result['type'],
                'name': result['name'],
                'relevance_score': result['relevance_score']
            })

        return Response(results)


    def handle_customer_search(self, search):
        results = Customer.objects.annotate(
            type=Value('customer'),
            exact_match=Case(
                When(name__iexact=search, then=Value(3)),
                default=Value(0),
                output_field=IntegerField()
            ),
            starts_with_match=Case(
                When(name__istartswith=search, then=Value(2)),
                default=Value(0),
                output_field=IntegerField()
            ),
            contains_match=Case(
                When(name__icontains=search, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).annotate(
            relevance_score=(Value(0) +
                             F('exact_match') +
                             F('starts_with_match') +
                             F('contains_match'))
        ).values('name', 'type', 'relevance_score')
        return results

    def handle_restaurant_search(self, search):
        results = Restaurant.objects.annotate(
            type=Value('restaurant'),
            exact_match=Case(
                When(name__iexact=search, then=Value(3)),
                default=Value(0),
                output_field=IntegerField()
            ),
            starts_with_match=Case(
                When(name__istartswith=search, then=Value(2)),
                default=Value(0),
                output_field=IntegerField()
            ),
            contains_match=Case(
                When(name__icontains=search, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).annotate(
            relevance_score=(Value(0) +
                             F('exact_match') +
                             F('starts_with_match') +
                             F('contains_match'))
        ).values('name', 'type', 'relevance_score')
        return results