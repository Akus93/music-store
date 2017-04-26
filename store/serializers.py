from base64 import b64decode
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from rest_framework import serializers

from store.models import UserProfile, Product, Artist, Genre, RecordLabel, Review, Shipping, Payment, Order, OrderItem


class ImageBase64Field(serializers.ImageField):
    def to_internal_value(self, data):
        try:
            decoded_image = b64decode(data.split(',')[1])
        except TypeError:
            raise serializers.ValidationError('Niepoprawny format zdjęcia.')
        data = ContentFile(decoded_image, name=str(uuid4()) + '.png')
        return super(ImageBase64Field, self).to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        read_only_fields = ('email', 'username')


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ('user', 'city')

    def update(self, instance, validated_data):
        try:
            user_data = validated_data.pop('user')
        except KeyError:
            user_data = {}
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        if first_name:
            instance.user.first_name = first_name
        if last_name:
            instance.user.last_name = last_name
        if last_name or first_name:
            instance.user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        read_only_fields = fields


class ArtistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artist
        fields = ('name', 'slug')
        read_only_fields = fields


class RecordLabelShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecordLabel
        fields = ('name', 'slug')
        read_only_fields = fields


class ShippingShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shipping
        fields = ('name', 'slug')
        read_only_fields = fields


class ProductsListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()
    artist = ArtistSerializer()
    medium_type = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('genre', 'artist', 'title', 'slug', 'medium_type', 'release_date', 'image', 'price', 'stock')
        read_only_fields = fields


class ProductDetailSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()
    artist = ArtistSerializer()
    medium_type = serializers.StringRelatedField()
    label = RecordLabelShortSerializer()
    tags = serializers.ReadOnlyField(source='get_serializable_tags')

    class Meta:
        model = Product
        fields = ('genre', 'artist', 'title', 'slug', 'medium_type', 'medium_count', 'release_date', 'image',
                  'description', 'price', 'length', 'label', 'tags', 'stock')
        read_only_fields = fields


class ReviewSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer()

    class Meta:
        model = Review
        fields = ('author', 'product', 'parent', 'text', 'rate', 'created')


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer()

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')


class OrderDetailSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()
    shipping = ShippingShortSerializer()
    payment = serializers.StringRelatedField()
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('user', 'shipping', 'payment', 'total_price', 'address', 'zip_code', 'city', 'phone', 'state',
                  'created', 'items')


class OrderListSerializer(serializers.ModelSerializer):
    shipping = ShippingShortSerializer()
    payment = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ('id', 'shipping', 'payment', 'total_price', 'state', 'created')


class OrderItemCreateSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(queryset=Product.objects.all(), slug_field='slug')

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')


class OrderCreateSerizalizer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)
    shipping = serializers.SlugRelatedField(queryset=Shipping.objects.all(), slug_field='slug')
    payment = serializers.SlugRelatedField(queryset=Payment.objects.all(), slug_field='slug')

    class Meta:
        model = Order
        exclude = ('user', 'state', 'created')

    def create(self, validated_data):
        items = validated_data.pop('items')
        if not items:
            raise serializers.ValidationError({'items': 'Nie można złożyć pustego zamówienia.'})
        order = super(OrderCreateSerizalizer, self).create(validated_data)
        order_items = []
        for item in items:
            order_items.append(OrderItem(order=order, product=item['product'], quantity=item['quantity']))
            item['product'].stock -= item['quantity']
            item['product'].save()
        OrderItem.objects.bulk_create(order_items)
        return order
