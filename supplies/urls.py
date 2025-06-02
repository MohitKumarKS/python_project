from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('edit-supply/<str:supply_id>/', views.edit_supply, name='edit_supply'),
    path('manage-requests/', views.manage_requests, name='manage_requests'),
    path('disaster-reports/', views.disaster_reports, name='disaster_reports'),
    path('public-view/', views.public_view, name='public_view'),
    # Add other URLs as needed
]
