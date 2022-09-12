from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from commerce.admin import MerchantInline
from network.admin import NetworkerInline
from home.models import Project, Pic

class WebUserAdmin(UserAdmin):
    inlines = (MerchantInline, NetworkerInline)

class PicInline(admin.TabularInline):
    model = Pic

class ProjectAdmin(admin.ModelAdmin):
    model = Project
    inlines = (PicInline,)


admin.site.unregister(User)
admin.site.register(User, WebUserAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Pic)

