from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Merchant, Listing, Bid, Comment, Category

class ListingInline(admin.StackedInline):
    model = Listing
    fk_name = "merchant"
    extra = 0

class BidInline(admin.TabularInline):
    model = Bid
    extra = 0

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0

class CategoryInline(admin.ModelAdmin):
    model = Category
    extra = 0

class MerchantInline(admin.StackedInline):
    model = Merchant

class MerchantAdmin(admin.ModelAdmin):
    inlines = (ListingInline, CommentInline, BidInline)

class CategoryAdmin(admin.ModelAdmin):
    verbose_name_plural = 'categories'
    prepopulated_fields = {'slug': ('name',)}

class ListingAdmin(admin.ModelAdmin):
    inlines = [BidInline, CommentInline]
    filter_horizontal = ('category', )

class CommerceUserAdmin(UserAdmin):
    inlines = (MerchantInline,)

admin.site.register(Merchant, MerchantAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(Category, CategoryAdmin)
admin.site.unregister(User)
admin.site.register(User, CommerceUserAdmin)

