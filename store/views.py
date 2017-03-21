from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend

from store.models import Product
from store.serializers import ProductsListSerializer, ProductDetailSerializer


class ProductListView(ListAPIView):
    queryset = Product.objects.select_related('genre', 'artist', 'medium_type', 'label')
    serializer_class = ProductsListSerializer
    # throttle_classes = TODO (ProductThrottle, )
    filter_backends = (DjangoFilterBackend, )
    # filter_class = TODO ProductFilterSet
    # pagination_class = TODO ProductsPagination


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.select_related('genre', 'artist', 'medium_type', 'label')
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
