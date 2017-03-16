from django.db import models
from django.contrib.auth.models import User

from taggit.managers import TaggableManager


class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name='Użytkownik', on_delete=models.CASCADE)
    city = models.CharField(verbose_name='Miejscowość', max_length=128, blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Profil użytkownika'
        verbose_name_plural = 'Profile użytkowników'


class Artist(models.Model):
    name = models.CharField(verbose_name='Nazwa', max_length=128)
    slug = models.SlugField(max_length=192, db_index=True, unique=True)


class Genre(models.Model):
    name = models.CharField(verbose_name='Nazwa', max_length=128)
    slug = models.SlugField(max_length=192, db_index=True, unique=True)


class Product(models.Model):
    FORMAT = (
        ('CD', 'CD'),
        ('DVD', 'DVD'),
        ('Vinyl', 'Vinyl'),
        ('Blu-ray', 'Blu-ray')
    )
    category = models.ForeignKey(Genre, verbose_name='Gatunek', related_name='products')
    artist = models.ForeignKey(Artist, verbose_name='Artysta', related_name='products')
    name = models.CharField(verbose_name='Nazwa', max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    format = models.CharField(max_length=8, choices=FORMAT, default='CD')
    release_date = models.DateField(verbose_name='Data wydania')
    image = models.ImageField(verbose_name='Okładka', upload_to='images', max_length=255, blank=True)
    description = models.TextField(verbose_name='Opis', max_length=1024, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    length = models.PositiveSmallIntegerField('Czas trwania', blank=True)
    label = models.CharField(verbose_name='Wytwórnia', max_length=128, blank=True)
    tags = TaggableManager()
    stock = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data dodania')

    class Meta:
        ordering = ('-created',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(UserProfile, db_index=False, verbose_name='Autor', related_name='reviews')
    product = models.ForeignKey(Product, db_index=True, verbose_name='Produkt', related_name='reviews')
    parent = models.ForeignKey('self', db_index=False, verbose_name='Rodzic', null=True, default=None)
    text = models.CharField(verbose_name='Tekst', max_length=255)
    rate = models.SmallIntegerField(verbose_name='Ocena', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])
    is_active = models.BooleanField(verbose_name='Czy aktywny', default=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name='Data dodania')

    def __str__(self):
        return 'Opinia {} o {}'.format(self.author, self.product)

    class Meta:
        verbose_name = 'Komentarz'
        verbose_name_plural = 'Komentarze'
