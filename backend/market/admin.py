from django.contrib import admin

from .models import Schedule, StoreHouse, Manufacturer, ProductCategory, Product, ProductModification, Order, CartProduct, Cart
# Register your models here.


admin.site.register(Schedule)
admin.site.register(StoreHouse)
admin.site.register(Manufacturer)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(ProductModification)
admin.site.register(Order)
admin.site.register(CartProduct)
admin.site.register(Cart)