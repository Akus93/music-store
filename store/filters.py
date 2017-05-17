from django_filters.rest_framework import FilterSet
from django_filters import CharFilter, NumberFilter, OrderingFilter, Filter

from store.models import Product, Review


class TagsFilter(Filter):

    def filter(self, qs, value):
        if not value:
            return qs
        self.lookup_expr = 'in'
        return super(TagsFilter, self).filter(qs, [value])


class ProductFilterSet(FilterSet):
    genre = CharFilter(name='genre__slug')
    artist = CharFilter(name='artist__slug')
    medium_type = CharFilter(name='medium_type__name')
    min_price = NumberFilter(name='price', lookup_expr='gte')
    max_price = NumberFilter(name='price', lookup_expr='lte')
    label = CharFilter(name='label__slug')
    ordering = OrderingFilter(fields=(('price', 'price'), ('-price', '-price')))
    tags = TagsFilter(name='tags__name')

    class Meta:
        model = Product
        fields = ('genre', 'artist', 'medium_type', 'min_price', 'max_price', 'label', 'ordering', 'tags')


class ReviewFilterSet(FilterSet):
    product = CharFilter(name='product__slug')

    class Meta:
        model = Review
        fields = ('product', )
