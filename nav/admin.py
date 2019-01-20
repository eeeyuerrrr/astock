from django.contrib import admin
from .models import Site


class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'icon', 'url', 'description', 'order')
    search_fields = ('name', 'category', 'description')
    list_filter = ('category',)
    ordering = ('order',)
    list_per_page = 30


admin.site.register(Site, SiteAdmin)
