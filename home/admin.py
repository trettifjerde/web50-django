from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from commerce.admin import MerchantInline
from network.admin import NetworkerInline

class WebUserAdmin(UserAdmin):
    inlines = (MerchantInline, NetworkerInline)

admin.site.unregister(User)
admin.site.register(User, WebUserAdmin)

