from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response

from store.paginations import StandardResultsSetPagination
from store.filters import ProductFilterSet
from store.models import Product, Review, Order, BankInfo
from store.utils import send_email_about_order
from store.throttles import ProductDetailThrottle, ProductListThrottle
from store.serializers import ProductsListSerializer, ProductDetailSerializer, ReviewSerializer, OrderDetailSerializer, \
    OrderListSerializer, OrderCreateSerizalizer, BankInfoSerializer


class ProductListView(ListAPIView):
    queryset = Product.objects.select_related('genre', 'artist', 'medium_type', 'label')
    serializer_class = ProductsListSerializer
    throttle_classes = (ProductListThrottle, )
    filter_backends = (DjangoFilterBackend, )
    filter_class = ProductFilterSet
    pagination_class = StandardResultsSetPagination


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.select_related('genre', 'artist', 'medium_type', 'label')
    serializer_class = ProductDetailSerializer
    throttle_classes = (ProductDetailThrottle, )
    lookup_field = 'slug'


class ProductRewievsListView(ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product__slug=self.kwargs['slug'], is_active=True)


class OrdersListView(ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = OrderListSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user.profile)


class OrderDetailView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk, *args, **kwargs):
        try:
            order = Order.objects.prefetch_related('items').get(id=pk, user=request.user.profile)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(OrderDetailSerializer(order).data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        try:
            order = Order.objects.prefetch_related('items').get(id=pk, user=request.user.profile)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if order.state != Order.ORDERED:
            return Response({'error': 'Zamówienie zostało już opłacone i nie może zostać usunięte,'
                                      ' prosimy o kontakt osobisty.'}, status=status.HTTP_400_BAD_REQUEST)
        for item in order.items.all():
            item.delete()
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = OrderCreateSerizalizer
    queryset = Order.objects.all().select_related('user__user')

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                order = serializer.save(user=self.request.user.profile)
                transaction.on_commit(lambda: send_email_about_order(order))
        except IntegrityError:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        payment_method = serializer.data.get('payment', None)
        if payment_method == 'przelew-bankowy':
            bank_info = BankInfo.objects.first()
            body = {'order': serializer.data, 'info': BankInfoSerializer(bank_info).data}
            return Response(body, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
