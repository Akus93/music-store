from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from store.models import UserProfile, Artist, Genre, Product, Review, Shipping, Medium, RecordLabel, Payment, Order,\
                         OrderItem


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, )


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'medium_type', 'medium_count', 'artist', 'label', 'stock')
    list_filter = ('artist', 'medium_type')
    list_select_related = ('medium_type', 'artist', 'genre', 'label')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'release_date'


class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'product', 'parent', 'rate')
    list_select_related = ('author', 'author__user', 'product')
    search_fields = ('author',)


class ShippingAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class RecordLabelAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'shipping', 'payment', 'total_price', 'state')
    list_filter = ('shipping', 'payment', 'state')
    list_editable = ('state',)
    list_select_related = ('user', 'user__user', 'shipping', 'payment')
    date_hierarchy = 'created'
    readonly_fields = ('total_price', 'created')
    search_fields = ('user__user__username',)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity')
    list_select_related = ('order', 'product')
    search_fields = ('id',)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Shipping, ShippingAdmin)
admin.site.register(RecordLabel, RecordLabelAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)

admin.site.register([Medium, Payment])
