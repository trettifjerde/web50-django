import os
from datetime import datetime
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from web50.settings import MEDIA_ROOT

LISTING_STORAGE = "commerce/listings/"

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

    def get_absolute_url(self):
        return reverse('commerce:category', kwargs={'slug': self.slug})

    def has_open_listings(self):
        return self.listings.filter(winner=None)

class Listing(models.Model):
    class Meta:
        ordering = ['-created']

    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.IntegerField()
    winner = models.ForeignKey(Merchant, null=True, default=None, blank=True, on_delete=models.SET_NULL, related_name="won_lots")
    image = models.ImageField(upload_to=LISTING_STORAGE, blank=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, related_name="listings")
    created = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, blank=True, related_name="listings")
    watchlist = models.ManyToManyField(Merchant, related_name="watchlist", blank=True)

    def __str__(self):
        return f'Listing "{self.title}" ({"closed" if self.winner else "open"})'

    def get_absolute_url(self):
        return reverse('commerce:listing', kwargs={'pk': self.pk})
    
    def current_bid_price(self):
        return self.bids.first().price if self.bids.count() else self.starting_bid

    def current_bid_merchant(self):
        return self.bids.first().merchant if self.bids.count() else None

    def prep_image(self):
        img = Image.open(self.image.file.file)
        img.thumbnail((600, 600))
        img_file = BytesIO()
        img.save(img_file, img.format)

        new_name = f'{datetime.now().timestamp()}.{img.format}'

        self.image.save(
            new_name,
            InMemoryUploadedFile(img_file, None, None, self.image.file.content_type, img.size, self.image.file.charset),
            save=False
        )

class Bid(models.Model):
    class Meta:
        ordering = ['-price']

    price = models.IntegerField()
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