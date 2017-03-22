from rest_framework.throttling import UserRateThrottle


class ProductDetailThrottle(UserRateThrottle):

    rate = '30/m'
    scope = 'product-detail'

    def allow_request(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return super(ProductDetailThrottle, self).allow_request(request, view)


class ProductListThrottle(UserRateThrottle):

    rate = '20/m'
    scope = 'product-detail'

    def allow_request(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return super(ProductListThrottle, self).allow_request(request, view)
