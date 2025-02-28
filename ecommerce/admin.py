from django.contrib import admin

from .models import NutrientCategory,Product,ProductCategory

admin.site.register(NutrientCategory),
admin.site.register(Product),
admin.site.register(ProductCategory)