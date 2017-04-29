from decimal import Decimal
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models import Sum

from taggit.managers import TaggableManager
from store.validators import validate_zip_code


class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name='Użytkownik', on_delete=models.CASCADE, related_name='profile')
    address = models.CharField(verbose_name='Adres', max_length=255,  blank=True, null=True)
    zip_code = models.CharField(verbose_name='Kod pocztowy', validators=[validate_zip_code], max_length=6,
                                blank=True, null=True)
    city = models.CharField(verbose_name='Miejscowość', max_length=128, blank=True, null=True)
    phone = models.CharField(verbose_name='Numer telefonu', max_length=16, blank=True, null=True)

    class Meta:
        verbose_name = 'Profil użytkownika'
        verbose_name_plural = 'Profile użytkowników'

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Artist(models.Model):
    """e.g Adele"""
    name = models.CharField(verbose_name='Nazwa', max_length=128)
    slug = models.SlugField(max_length=192, db_index=True, unique=True)

    class Meta:
        index_together = (('id', 'slug'),)
        verbose_name = 'Artysta'
        verbose_name_plural = 'Artyści'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """e.g Pop"""
    name = models.CharField(verbose_name='Nazwa', max_length=128)
    slug = models.SlugField(max_length=192, db_index=True, unique=True)

    class Meta:
        index_together = (('id', 'slug'),)
        verbose_name = 'Gatunek'
        verbose_name_plural = 'Gatunki'

    def __str__(self):
        return self.name


class RecordLabel(models.Model):
    """e.g. Sony Music Entertainment"""
    name = models.CharField(verbose_name='Nazwa', max_length=128)
    slug = models.SlugField(max_length=192, db_index=True, unique=True)
    description = models.TextField(verbose_name='Opis', max_length=1024, blank=True, null=True)

    class Meta:
        index_together = (('id', 'slug'),)
        verbose_name = 'Wytwórnia muzyczna'
        verbose_name_plural = 'Wytwórnie muzyczne'

    def __str__(self):
        return self.name


class Medium(models.Model):
    """e.g CD"""
    name = models.CharField(verbose_name='Nazwa', max_length=128)

    class Meta:
        verbose_name = 'Nośnik'
        verbose_name_plural = 'Nośniki'

    def __str__(self):
        return self.name


class Product(models.Model):
    genre = models.ForeignKey(Genre, verbose_name='Gatunek', related_name='products')
    artist = models.ForeignKey(Artist, verbose_name='Artysta', related_name='products', blank=True, null=True)
    title = models.CharField(verbose_name='Tytuł', max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    medium_type = models.ForeignKey(Medium, verbose_name='Rodzaj nośnika', related_name='products')
    medium_count = models.PositiveSmallIntegerField(verbose_name='Liczba nośników', default=1)
    release_date = models.DateField(verbose_name='Data wydania')
    image = models.ImageField(verbose_name='Okładka', upload_to='images', max_length=255, blank=True, null=True)
    description = models.TextField(verbose_name='Opis', max_length=1024, blank=True, null=True)
    price = models.DecimalField(verbose_name='Cena', max_digits=5, decimal_places=2)
    length = models.PositiveSmallIntegerField('Czas trwania', blank=True, null=True)
    label = models.ForeignKey(RecordLabel, verbose_name='Wytwórnia', related_name='products', blank=True, null=True)
    tags = TaggableManager(verbose_name='Tagi', blank=True)
    stock = models.PositiveIntegerField(verbose_name='Dostępność')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data dodania')

    class Meta:
        ordering = ('-created',)
        index_together = (('id', 'slug'),)
        verbose_name = 'Produkt'
        verbose_name_plural = 'Produkty'

    def __str__(self):
        return self.title

    def get_serializable_tags(self):
        return self.tags.values_list('name', flat=True)


class Review(models.Model):
    author = models.ForeignKey(UserProfile, db_index=False, verbose_name='Autor', related_name='reviews')
    product = models.ForeignKey(Product, db_index=True, verbose_name='Produkt', related_name='reviews')
    parent = models.ForeignKey('self', db_index=False, verbose_name='Rodzic', null=True, default=None, blank=True)
    text = models.CharField(verbose_name='Tekst', max_length=255)
    rate = models.PositiveSmallIntegerField(verbose_name='Ocena', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    is_active = models.BooleanField(verbose_name='Czy aktywny', default=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data dodania')

    class Meta:
        verbose_name = 'Komentarz'
        verbose_name_plural = 'Komentarze'

    def __str__(self):
        return 'Opinia {} o {}'.format(self.author, self.product)


class Shipping(models.Model):
    """e.g InPost"""
    name = models.CharField(verbose_name='Nazwa', max_length=192)
    slug = models.SlugField(max_length=255, db_index=True, unique=True)
    price = models.DecimalField(verbose_name='Cena', max_digits=5, decimal_places=2)

    class Meta:
        index_together = (('id', 'slug'),)
        verbose_name = 'Dostawa'
        verbose_name_plural = 'Dostawy'

    def __str__(self):
        return self.name


class Payment(models.Model):
    """e.g PayPal"""
    name = models.CharField(verbose_name='Nazwa', max_length=192)
    slug = models.SlugField(max_length=255, db_index=True, unique=True)

    class Meta:
        verbose_name = 'Płatność'
        verbose_name_plural = 'Płatności'
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name


class Order(models.Model):
    ORDERED = 1
    PAID = 2
    SEND = 3
    STATES = (
        (ORDERED, 'Zamówione'),
        (PAID, 'Opłacone'),
        (SEND, 'Wysłane')
    )
    user = models.ForeignKey(UserProfile, verbose_name='Kupujący', related_name='orders')
    code = models.UUIDField(default=uuid4, editable=False)
    shipping = models.ForeignKey(Shipping, verbose_name='Dostawa', related_name='orders')
    payment = models.ForeignKey(Payment, verbose_name='Płatonść', related_name='orders')
    address = models.CharField(verbose_name='Adres', max_length=255)
    zip_code = models.CharField(verbose_name='Kod pocztowy', validators=[validate_zip_code], max_length=6)
    city = models.CharField(verbose_name='Miejscowość', max_length=128)
    phone = models.CharField(verbose_name='Numer telefonu', max_length=16, blank=True, null=True)
    state = models.PositiveSmallIntegerField(verbose_name='Status', choices=STATES, default=ORDERED)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')

    def total_price(self):
        return self.shipping.price + Decimal(self.items.aggregate(total_price=Sum(F('quantity')*F('product__price'),
                                                                  output_field=models.DecimalField()))['total_price'])
    total_price.short_description = 'Cena całkowita'

    class Meta:
        verbose_name = 'Zamówienie'
        verbose_name_plural = 'Zamówienia'
        ordering = ['-created']

    def __str__(self):
        return 'Zamówienie nr. {}'.format(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Zamówienie', related_name='items')
    product = models.ForeignKey(Product, verbose_name='Produkt')
    quantity = models.PositiveSmallIntegerField(verbose_name='Liczba')

    class Meta:
        verbose_name = 'Zamówiony produkt'
        verbose_name_plural = 'Zamówione produkty'

    def __str__(self):
        return 'Zamówiony produkt nr. {}'.format(self.id)


class BankInfo(models.Model):
    account = models.CharField(verbose_name='Numer rachunku', max_length=100)
    name = models.CharField(verbose_name='Nazwa odbiorcy', max_length=128)
    address = models.CharField(verbose_name='Adres', max_length=255)

    class Meta:
        verbose_name = 'Dane przelewowe'
        verbose_name_plural = 'Dane przelewowe'

    def __str__(self):
        return 'Dane przelewowe'
