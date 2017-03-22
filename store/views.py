from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response

from store.models import Product, Review, Order, OrderItem
from store.serializers import ProductsListSerializer, ProductDetailSerializer, ReviewSerializer, OrderSerializer


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


class ProductRewievsListView(ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product__slug=self.kwargs['slug'], is_active=True)


class OrderDetailView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, id, *args, **kwargs):
        try:
            order = Order.objects.prefetch_related('items').get(id=id, user=request.user.profile)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
