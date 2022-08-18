from django.contrib import admin
from .models import Networker, NetworkPost

class NetworkPostAdmin(admin.ModelAdmin):
    model = NetworkPost

class NetworkerAdmin(admin.ModelAdmin):
    model = Networker

class NetworkerInline(admin.StackedInline):
    model = Networker

admin.site.register(Networker, NetworkerAdmin)
admin.site.register(NetworkPost, NetworkPostAdmin)
