from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('delete/', views.delete_transaction, name='delete_transaction'),
    path('change/', views.change_transaction, name='change_transaction'),
]