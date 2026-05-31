from django.contrib import admin
from .models import Category, Transaction, UserData
# Register your models here.


admin.site.register(UserData)
admin.site.register(Category)
admin.site.register(Transaction)
