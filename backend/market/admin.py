from django.contrib import admin

from .models import Schedule, StoreHouse, Manufacturer, ProductCategory, Product, ProductModification, Order, CartProduct, Cart
# Register your models here.


admin.site.register(Order)
admin.site.register(CartProduct)
admin.site.register(Cart)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['start_time', 'end_time']


@admin.register(StoreHouse)
class StoreHouseAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'available']
    list_editable = ['available']


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'available']
    list_editable = ['available']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'manufacturer', 'category', 'store_house', 'available']
    list_editable = ['quantity', 'available']


@admin.register(ProductModification)
class ProductModificationAdmin(admin.ModelAdmin):
    list_display = ['product', 'specifications', 'price', 'quantity', 'available']
    list_editable = ['price', 'quantity', 'available']