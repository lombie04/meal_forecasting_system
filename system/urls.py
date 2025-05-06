from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('redirect/', views.role_based_redirect, name='role_redirect'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('chef_dashboard/', views.chef_dashboard, name='chef_dashboard'),
    path('place_order/<int:forecast_id>/', views.place_order, name='place_order'),
    path('view-current-stock/', views.view_current_stock, name='view_current_stock'),
    path('audit_dashboard/', views.audit_dashboard, name='audit_dashboard'),
    path('stock_management/', views.stock_management, name='stock_management'),
    path('accounts_dashboard/', views.accounts_dashboard, name='accounts_dashboard'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('place_order/<int:forecast_id>/', views.place_order, name='place_order'),
    path('profile/', views.profile_view, name='profile_view'),
    path('accounts/edit/', views.edit_profile, name='edit_profile'),
    path('app_admin/add_user/', views.add_user_page, name='add_user_page'),
    path('app_admin/delete_user/', views.delete_user_page, name='delete_user_page'),
    path('app_admin/edit_user/', views.edit_user, name='edit_user'),
    path('app_admin/system_summary/', views.system_summary_page, name='system_summary_page'),
    path('verify_audit_access/', views.verify_audit_access, name='verify_audit_access'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('edit_user/<int:user_id>/', views.edit_user_profile, name='edit_user_profile'),
]
