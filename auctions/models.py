from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError


class User(AbstractUser):
    # Extends abstract user, so it comes with most default behavior.
    id = models.AutoField(primary_key=True)

def validate_price(value):
    if value < 0:
        raise ValidationError('Price must be positive') 

class Listing(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True) # Holds the timestamp for the listing's creation
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    price = models.DecimalField(decimal_places=2, max_digits=10, validators=[validate_price])
    image_url = models.URLField(blank=True)
    CATEGORIES = [
        ('TOY', 'Toys'),
        ('ELC', 'Electronics'),
        ('HOM', 'Home'),
        ('TOO', 'Tools'),
    ]
    category = models.CharField(max_length=3, choices=CATEGORIES, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, auto_created=True)
    watchers = models.ManyToManyField(User, related_name='watchlist', blank=True, default=None, auto_created=True)
    winner = models.ForeignKey(User, on_delete=models.SET_DEFAULT, null=True, blank=True, default=None, related_name='listings_won')

class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10, validators=[validate_price])
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=500)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    timestamp = models.DateTimeField(auto_now_add=True) # Holds the timestamp for the listing's creation