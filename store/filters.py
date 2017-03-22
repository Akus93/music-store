from django_filters.rest_framework import FilterSet
from django_filters import CharFilter, NumberFilter

from store.models import Product


class ProductFilterSet(FilterSet):
    genre = CharFilter(name='genre__slug')
    artist = CharFilter(name='artist__slug')
    medium_type = CharFilter(name='medium_type__name')
    min_price = NumberFilter(name='price', lookup_expr='gte')
    max_price = NumberFilter(name='price', lookup_expr='lte')
    label = CharFilter(name='label__slug')

    class Meta:
        model = Product
        fields = ('genre', 'artist', 'medium_type', 'min_price', 'max_price', 'label')
