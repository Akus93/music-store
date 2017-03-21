from rest_framework import serializers

from store.models import Product, Artist, Genre, RecordLabel


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

    class Meta:
        model = Product
        fields = ('genre', 'artist', 'title', 'slug', 'medium_type', 'medium_count', 'release_date', 'image',
                  'description', 'price', 'length', 'label', 'tags', 'stock')
        read_only_fields = fields
