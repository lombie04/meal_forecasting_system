from django.contrib import admin
from .models import Meal, StockItem,MealIngredient, GuestForeCast, StockOrder, StockMovementLog, UserProfile

class MealIngredientInline(admin.TabularInline):
    model = MealIngredient
    extra = 1
class MealAdmin(admin.ModelAdmin):
    inlines = [MealIngredientInline]
    list_display = ['name', 'cost_per_portion']
    fields = ['name', 'cost_per_portion']
    
admin.site.register(Meal, MealAdmin)
admin.site.register(MealIngredient)
admin.site.register(StockItem)
admin.site.register(GuestForeCast)
admin.site.register(StockOrder)
admin.site.register(StockMovementLog)
admin.site.register(UserProfile)