from django.db import models
from django.contrib.auth.models import User

class Meal(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ingredients = models.ManyToManyField('StockItem', through='MealIngredient')
    cost_per_portion = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return self.name

class MealIngredient(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    stock_item = models.ForeignKey('StockItem', on_delete=models.CASCADE)
    quantity_per_person = models.FloatField()
    def __str__(self):
        return f"{self.stock_item.product_name} for {self.meal.name}"
    
class StockItem(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilograms'),
        ('pcs', 'Pieces'),
        ('ltr', 'Liters'),
        ('g', 'Grams'),
    ]
    product_name = models.CharField(max_length=100)
    product_id = models.CharField(max_length=50, unique=True)
    available_quantity = models.FloatField(default=0)
    unit_of_measurement = models.CharField(max_length=10, choices=UNIT_CHOICES)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return f"{self.product_name} ({self.product_id})"
        
class GuestForeCast(models.Model):
    chef_name = models.CharField(max_length=100)
    chef_id = models.CharField(max_length=50)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    number_of_guests = models.PositiveIntegerField()
    forecasted_quantity = models.PositiveIntegerField(help_text="Auto-calculated: guests * portion size")
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    shift = models.CharField(max_length=20, choices=[
    ('breakfast', 'Breakfast'),
    ('lunch', 'Lunch'),
    ('dinner', 'Dinner'),
    ('night', 'Night Shift')
], default='lunch')
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed')
    ], default='pending')
    def __str__(self):
        return (f"Name of Chef: {self.chef_name} (ID: {self.chef_id}) | "f"Guests: {self.number_of_guests} | Forecast: {self.forecasted_quantity}g | "f"Meal: {self.meal.name} for ({self.shift})")   
class ForecastIngredient(models.Model):
    forecast = models.ForeignKey(GuestForeCast, on_delete=models.CASCADE, related_name='ingredients')
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE)
    qty_per_person = models.FloatField()
    def total_quantity(self):
        return self.qty_per_person * self.forecast.number_of_guests    
class StockOrder(models.Model):
    chef_name = models.CharField(max_length=100)
    order_datetime = models.DateTimeField(auto_now_add=True)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity_requested = models.PositiveIntegerField(help_text="Quantity requested in grams or units")
    fulfilled = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.chef_name} | {self.meal.name} | {self.quantity_requested} units | Fulfilled: {self.fulfilled}"
    
class StockMovementLog(models.Model):
    product_name = models.CharField(max_length=100)
    quantity_before = models.PositiveIntegerField()
    quantity_issued = models.PositiveIntegerField()
    quantity_after = models.PositiveIntegerField()
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    issued_by = models.CharField(max_length=100)
    def __str__(self):
        return (f"{self.product_name} | Before: {self.quantity_before} | "
                f"Issued: {self.quantity_issued} | After: {self.quantity_after} | "
                f"Issued by: {self.issued_by} on {self.date} {self.time}")

class UserProfile(models.Model):
    ROLE_CHOICES= [
        ('admin', 'Admin'),
        ('chef', 'Chef'),
        ('accounts', 'Accounts Officer'),
        ('audit', 'Audit'),
        ('manager', 'Hospitality Manager')
    ]   
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)  
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class SystemLog(models.Model):
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('meal_request', 'Meal Request'),
        ('other', 'Other')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"
