from django.contrib import admin
from .models import Stock, Industry


class IndustryStockRelationInline(admin.TabularInline):
    model = Industry.stocks.through
    extra = 1

    readonly_fields = ('stock',)

    def get_queryset(self, request):
        qs = super(IndustryStockRelationInline, self).get_queryset(request)
        return qs.select_related('stock')


class StockAdmin(admin.ModelAdmin):
    inlines = [ IndustryStockRelationInline, ]
    list_display = ('name', 'code', 'market_name', 'isindex')
    search_fields = ('name', 'code')
    list_per_page = 30


class IndustryAdmin(admin.ModelAdmin):
    inlines = [ IndustryStockRelationInline, ]
    exclude = ('stocks',)
    list_display = ('name', 'stock_count','order')
    search_fields = ('name',)
    list_per_page = 30
    ordering = ('order',)

    def get_queryset(self, request):
        qs = super(IndustryAdmin, self).get_queryset(request)
        return qs.prefetch_related('stocks')


admin.site.register(Stock, StockAdmin)
admin.site.register(Industry, IndustryAdmin)
