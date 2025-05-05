from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import GuestForeCastForm, StockItemForm, EditUserForm
from .models import GuestForeCast, Meal, ForecastIngredient, SystemLog
from django.shortcuts import get_object_or_404
from .models import StockOrder, StockMovementLog, MealIngredient, StockItem
from django.contrib.auth.models import User
from datetime import date
from django.utils.dateparse import parse_date
from django.contrib import messages
from decimal import Decimal
from django.db.models import Sum
from datetime import datetime
from system.models import SystemLog
from collections import Counter, defaultdict
@login_required
def role_based_redirect(request):
    user_profile = UserProfile.objects.get(user=request.user)
    role = user_profile.role
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'chef':
        return redirect('chef_dashboard')
    elif role == 'audit':
        return redirect('audit_dashboard')
    elif role == 'accounts':
        return redirect('accounts_dashboard')
    elif role == 'manager':
        return redirect('manager_dashboard')
    else:
        return redirect('admin:index')
@login_required
def admin_dashboard(request):
    try:
        if request.user.userprofile.role != 'admin':
            return redirect('unauthorized')
    except UserProfile.DoesNotExist:
        return redirect('unauthorized')
    users = User.objects.all().select_related('userprofile')
    roles = ['admin', 'chef', 'audit', 'accounts', 'manager']
    users_by_role = {role: [] for role in roles}
    for user in users:
        try:
            role = user.userprofile.role
            users_by_role[role].append(user)
        except UserProfile.DoesNotExist:
            continue
    total_meals = GuestForeCast.objects.count()
    total_guests = GuestForeCast.objects.aggregate(total=Sum('number_of_guests'))['total'] or 0
    total_stock = StockItem.objects.count()
    if request.method == 'POST':
        from .forms import CreateUserForm
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New user created successfully.')
            return redirect('admin_dashboard')
    else:
        from .forms import CreateUserForm
        form = CreateUserForm()
    system_logs = SystemLog.objects.order_by('-timestamp')[:50]
    return render(request, 'admin_dashboard.html', {
        'users_by_role': users_by_role,
        'form': form,
        'total_meals': total_meals,
        'total_guests': total_guests,
        'total_stock': total_stock,
        'system_logs': system_logs,
        'year': datetime.now().year
    })
@login_required
def manage_users(request):
    if request.user.userprofile.role != 'admin':
        return redirect('unauthorized')
    users = User.objects.select_related('userprofile').all().order_by('username')
    return render(request, 'admin_actions/manage_users.html', {
        'users': users,
    })
@login_required
def edit_user_profile(request, user_id):
    if user_id == 1:
        messages.error(request, "This user (Master ID) cannot be edited for safety reasons.")
        return redirect('manage_users')
    if request.user.userprofile.role != 'admin':
        return redirect('unauthorized')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user, user_instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{user.username}' updated successfully.")
            return redirect('manage_users')
    else:
        form = EditUserForm(instance=user, user_instance=user)
    return render(request, 'admin_actions/edit_user_profile.html', {
        'form': form,
        'user_obj': user,
    })
def chef_dashboard(request):
    if request.method == 'POST':
        meal_id = request.POST.get('meal')
        shift = request.POST.get('shift')
        number_of_guests = int(request.POST.get('number_of_guests'))
        try:
            meal = Meal.objects.get(id=meal_id)
        except Meal.DoesNotExist:
            messages.error(request, "Selected meal does not exist.")
            return redirect('chef_dashboard')
        forecast = GuestForeCast.objects.create(
            chef_name=request.user.username,
            chef_id=request.user.id,
            meal=meal,
            shift=shift,
            number_of_guests=number_of_guests,
            forecasted_quantity=0,
            status='pending'
        )
        total_quantity = 0
        for meal_ingredient in meal.mealingredient_set.all():
            stock_item = meal_ingredient.stock_item
            qty_per_person = meal_ingredient.quantity_per_person
            total_qty_needed = qty_per_person * number_of_guests
            stock_item.available_quantity -= total_qty_needed
            stock_item.save()
            ForecastIngredient.objects.create(
                forecast=forecast,
                stock_item=stock_item,
                qty_per_person=qty_per_person
            )
            total_quantity += total_qty_needed
        forecast.forecasted_quantity = total_quantity
        forecast.save()
        SystemLog.objects.create(
            user=request.user,
            action='meal_request',
            description=f"{request.user.username} requested meal '{meal.name}' for {number_of_guests} guests"
        )
        messages.success(request, "Forecast submitted and stock deducted.")
        return redirect('chef_dashboard')
    else:
        form = GuestForeCastForm()
        forecasts = GuestForeCast.objects.filter(chef_name=request.user.username)
        stock = StockItem.objects.all()
        placed_orders = StockOrder.objects.values_list('meal__id', flat=True)
        placed_forecast_ids = [f.id for f in forecasts if f.meal.id in placed_orders]
    return render(request, 'chef_dashboard.html', {
        'form': form,
        'forecasts': forecasts,
        'stock': stock,
        'placed_orders': placed_forecast_ids,
        'meals': Meal.objects.all()
    })
@login_required
def audit_dashboard(request):
    if not request.session.get('audit_verified'):
        return redirect('verify_audit_access')
    logs = StockMovementLog.objects.all().order_by('-date', '-time')
    forecasts = GuestForeCast.objects.all().order_by('-date')
    orders = StockOrder.objects.all().order_by('-order_datetime')
    stock = StockItem.objects.all()
    return render(request, 'audit_dashboard.html', {
        'logs': logs,
        'forecasts': forecasts,
        'orders': orders,
        'stock': stock
    })
@login_required
def accounts_dashboard(request):
    orders = StockOrder.objects.all().order_by('-order_datetime')
    meal_filter = request.GET.get('meal')
    shift_filter = request.GET.get('shift')
    date_filter = request.GET.get('date')
    if date_filter:
        parsed_date = parse_date(date_filter)
        if parsed_date:
            orders = orders.filter(order_datetime__date=parsed_date)
    meal_summary = {}
    total_revenue = 0
    if meal_filter:
        orders = orders.filter(meal__name__icontains=meal_filter)
    if shift_filter:
        forecast_ids = GuestForeCast.objects.filter(
        shift__icontains=shift_filter
        ).values_list('id', flat=True)
        orders = orders.filter(meal__guestforecast__id__in=forecast_ids)
    for order in orders:
        meal = order.meal
        cost = meal.cost_per_portion or 0
        qty = order.quantity_requested
        meal_summary.setdefault(meal.name, {'quantity': 0, 'revenue': 0})
        meal_summary[meal.name]['quantity'] += qty
        meal_summary[meal.name]['revenue'] += cost * qty
        total_revenue += cost * qty
    daily_revenue = defaultdict(Decimal)
    for order in orders:
        meal = order.meal
        cost = meal.cost_per_portion or 0
        date_key = order.order_datetime.date()
        daily_revenue[date_key] += cost * order.quantity_requested
    revenue_dates = [str(date) for date in sorted(daily_revenue.keys())]
    revenue_values = [round(daily_revenue[date], 2) for date in sorted(daily_revenue.keys())]
    
    meal_names = []
    revenues = []
    for meal_name, summary in meal_summary.items():
        meal_names.append(meal_name)
        revenues.append(float(summary['revenue']))
    return render(request, 'accounts_dashboard.html', {
        'orders': orders,
        'meal_summary': meal_summary,
        'total_revenue': total_revenue,
        'date_filter': date_filter,
        'meal_names': meal_names,
        'revenues': revenues,
        'revenue_dates': revenue_dates,
        'revenue_values': revenue_values,
    })
@login_required
def manager_dashboard(request):
    today = date.today()
    if request.method == 'POST' and 'meal_name' in request.POST:
        meal_name = request.POST.get('meal_name')
        cost_per_portion = request.POST.get('cost_per_portion')
        ingredients = request.POST.getlist('ingredient')
        quantities = request.POST.getlist('quantity')
        if meal_name and cost_per_portion and ingredients:
            meal = Meal.objects.create(
                name=meal_name,
                cost_per_portion=Decimal(cost_per_portion)
            )
            for item_id, qty in zip(ingredients, quantities):
                if item_id: 
                    stock_item = StockItem.objects.get(id=item_id)
                    MealIngredient.objects.create(
                        meal=meal,
                        stock_item=stock_item,
                        quantity_per_person=float(qty)
                    )
            messages.success(request, "Meal added successfully.")
            return redirect('manager_dashboard')
        else:
            messages.error(request, "Please fill all fields to add a meal.")
    forecasts = GuestForeCast.objects.filter(date__gte=today).order_by('date')
    date_filter = request.GET.get('date')
    chef_filter = request.GET.get('chef')
    meal_filter = request.GET.get('meal')
    if date_filter:
        forecasts = forecasts.filter(date=date_filter)
    if chef_filter:
        forecasts = forecasts.filter(chef_name__icontains=chef_filter)
    if meal_filter:
        forecasts = forecasts.filter(meal__name__icontains=meal_filter)
    meal_summary = {}
    for forecast in forecasts:
        meal_name = forecast.meal.name
        meal_summary.setdefault(meal_name, 0)
        meal_summary[meal_name] += forecast.number_of_guests
    total_forecasts = forecasts.count()
    total_guests = sum(f.number_of_guests for f in forecasts)
    total_chefs = len(set(f.chef_name for f in forecasts))
    shift_counts = Counter(f.shift for f in forecasts)
    chart_labels = list(shift_counts.keys())
    chart_data = list(shift_counts.values())
    return render(request, 'manager_dashboard.html', {
        'forecasts': forecasts,
        'meal_summary': meal_summary,
        'total_forecasts': total_forecasts,
        'total_guests': total_guests,
        'total_chefs': total_chefs,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'stock_items': StockItem.objects.all(),
    })
@login_required
def profile_view(request):
    return render(request, 'profile.html')
@login_required
def edit_profile(request):
    return render(request, 'edit_profile.html')

@login_required
def add_user_page(request):
    from .forms import CreateUserForm
    form = CreateUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User added successfully.')
        return redirect('admin_dashboard')
    return render(request, 'admin_actions/add_user_page.html', {'form': form})

@login_required
def delete_user_page(request):
    users = User.objects.exclude(username=request.user.username)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        User.objects.filter(id=user_id).delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('admin_dashboard')
    return render(request, 'admin_actions/delete_user_page.html', {'users': users})

def edit_user(request):
    if request.method == 'POST' and request.user.userprofile.role == 'admin':
        username = request.POST.get('username')
        new_role = request.POST.get('new_role')
        try:
            user = User.objects.get(username=username)
            profile = user.userprofile
            profile.role = new_role
            profile.save()
            messages.success(request, f"{username}'s role updated to {new_role}.")
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, "User not found or missing profile.")
        return redirect('admin_dashboard')
    else:
        return redirect('unauthorized')

def system_summary_page(request):
    total_users = User.objects.count()
    total_meals = Meal.objects.count()
    total_stock_items = StockItem.objects.count()
    total_guests = GuestForeCast.objects.aggregate(total=Sum('number_of_guests'))['total'] or 0
    meal_logs = SystemLog.objects.filter(action='meal_request').order_by('-timestamp')[:50]
    return render(request, 'admin_actions/system_summary.html', {
        'total_users': total_users,
        'total_meals': total_meals,
        'total_stock_items': total_stock_items,
        'total_guests': total_guests,
        'meal_logs': meal_logs,
        'year': datetime.now().year
    })
@login_required
def place_order(request, forecast_id):
    forecast = get_object_or_404(GuestForeCast, id=forecast_id)
    if forecast.status == 'completed':
        return redirect('chef_dashboard')
    errors = []
    for ingredient in forecast.ingredients.all():
        total_qty = ingredient.qty_per_person * forecast.number_of_guests
        stock_item = ingredient.stock_item
        if total_qty > stock_item.available_quantity:
            errors.append(f"Not enough {stock_item.product_name} in stock.")
    if errors:
        return redirect('chef_dashboard')
    for ingredient in forecast.ingredients.all():
        total_qty = ingredient.qty_per_person * forecast.number_of_guests
        stock_item = ingredient.stock_item
        quantity_before = stock_item.available_quantity
        stock_item.available_quantity -= total_qty
        stock_item.save()
        StockMovementLog.objects.create(
            product_name=stock_item.product_name,
            quantity_before=quantity_before,
            quantity_issued=total_qty,
            quantity_after=stock_item.available_quantity,
            issued_by=forecast.chef_name
        )
    forecast.status = 'completed'
    forecast.save()
    StockOrder.objects.create(
        chef_name=forecast.chef_name,
        meal=forecast.meal,
        quantity_requested=forecast.forecasted_quantity,
        fulfilled=True
    )
    return redirect('chef_dashboard')  
def view_current_stock(request):
    stock = StockItem.objects.all()
    return render(request, 'chef_view_stock.html', {'stock': stock})

def stock_management(request):
    if request.method == 'POST':
        form = StockItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock item added successfully.")
            return redirect('stock_management')
    else:
        form = StockItemForm()
    stock_items = StockItem.objects.all()
    
    context = {
        'form': form,
        'stock_items': stock_items,
    }
    return render(request, 'stock_management.html', context)
@login_required
def add_meal(request):
    if request.user.userprofile.role != 'manager':
        return redirect('unauthorized')

    stock_items = StockItem.objects.all()

    if request.method == 'POST':
        meal_name = request.POST.get('meal_name')
        ingredients = request.POST.getlist('ingredient')
        quantities = request.POST.getlist('quantity')

        if meal_name and ingredients:
            meal = Meal.objects.create(name=meal_name)
            for item_id, qty in zip(ingredients, quantities):
                stock_item = StockItem.objects.get(id=item_id)
                MealIngredient.objects.create(
                    meal=meal,
                    stock_item=stock_item,
                    quantity_per_person=float(qty)
                )
            messages.success(request, "Meal added successfully.")
            return redirect('manager_dashboard')
        else:
            messages.error(request, "Please provide a meal name and at least one ingredient.")

    return render(request, 'add_meal.html', {'stock_items': stock_items})
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
@login_required
def verify_audit_access(request):
    if request.method == 'POST':
        key = request.POST.get('access_code')
        if key == 'Schon Kaputt@04':
            request.session['audit_verified'] = True
            return redirect('audit_dashboard')
        else:
            messages.error(request, "Incorrect access code.")
            return redirect('verify_audit_access')
    else:
        return render(request, 'verify_audit.html')
