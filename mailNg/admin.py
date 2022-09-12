from django.contrib import admin
from .models import Email

class EmailNgAdmin(admin.ModelAdmin):
    model = Email

admin.site.register(Email, EmailNgAdmin)