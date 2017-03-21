from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from store.views import ProductListView, ProductDetailView


router = DefaultRouter()


urlpatterns = [
    url(r'^products/$', ProductListView.as_view()),
    url(r'^products/(?P<slug>[\w-]+)/$', ProductDetailView.as_view()),
    url(r'^', include(router.urls)),
]
