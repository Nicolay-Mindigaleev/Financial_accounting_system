from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add_tr/', views.add_transaction, name='add_transaction'),
    path('delete_tr/', views.delete_transaction, name='delete_transaction'),
    path('edit_tr/<int:pk>/', views.change_transaction, name='change_transaction'),
    path('add_category/', views.add_category, name='add_category'),
    path('delete_category/', views.delete_category, name='delete_category'),
    path('edit_category/', views.change_category, name='change_category'),
    path('report/', views.report, name='report'),
]
