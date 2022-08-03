from django.contrib.auth.models import User
from django.db import models

class Merchant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username}'

class Category(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(max_length=7)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    class Meta:
        ordering = ['-created']

    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.FloatField(default=0)
    winner = models.ForeignKey(Merchant, null=True, default=None, blank=True, on_delete=models.SET_NULL, related_name="won_lots")
    image = models.ImageField(upload_to="commerce/listings/", null=True, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="listings")
    created = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, blank=True, related_name="listings")
    watchlist = models.ManyToManyField(Merchant, related_name="watchlist", blank=True)

    def __str__(self):
        return f'Listing "{self.title}" ({"closed" if self.winner else "open"})'
    
    def get_current_bid_price(self):
        return self.bids.first().price if self.get_bids_length() else self.starting_bid

    def get_current_bid_merchant(self):
        return self.bids.first().merchant
    
    def get_bids_length(self):
        return self.bids.count()


class Bid(models.Model):
    class Meta:
        ordering = ['-price']

    price = models.FloatField()
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid: {self.price} on {self.listing}"

class Comment(models.Model):
    class Meta:
        ordering = ['created']
    text = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="comments")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment: by {self.merchant} on {self.listing}"