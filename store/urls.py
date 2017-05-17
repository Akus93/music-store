from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from store.views import ProductListView, ProductDetailView, ReviewView, OrderDetailView,\
                        OrdersListView, OrderCreateView, RetrieveCurrentUserProfile


router = DefaultRouter()


urlpatterns = [
    url(r'^products/$', ProductListView.as_view()),
    url(r'^products/(?P<slug>[\w-]+)/$', ProductDetailView.as_view()),
    url(r'^reviews/$', ReviewView.as_view()),
    url(r'^orders/$', OrdersListView.as_view()),
    url(r'^orders/new/$', OrderCreateView.as_view()),
    url(r'^orders/(?P<pk>[\d]+)/$', OrderDetailView.as_view()),
    url(r'^profile/$', RetrieveCurrentUserProfile.as_view()),
    url(r'^', include(router.urls)),
]
