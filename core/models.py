from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
# Create your models here.
class UserData(AbstractUser):
    pass
class Category(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, verbose_name="Пользователь",)
    category_id = models.AutoField(verbose_name="id категорий", primary_key=True)
    category_name = models.CharField(verbose_name="Названия категории", max_length=30)
    def __str__(self):
        return f"{self.category_id}, {self.user}"
class Transaction(models.Model):
    operation_types = [
                        ("Income", "Доход"),
                        ("Consumption", "Расход")
                    ]
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, verbose_name="Пользователь")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    operation = models.CharField(verbose_name="Тип операции", choices=operation_types, default="Consumption")
    transaction_sum = models.PositiveIntegerField(verbose_name="Сумма операции", validators=[MinValueValidator(1)])
    date = models.DateField(verbose_name="Дата операции")
    description = models.CharField(verbose_name="Описание", max_length=500, blank=True, null=True)
    def __str__(self):
        return f"{self.user}, {self.category}, {self.operation}, {self.transaction_sum}, {self.date}, {self.description}"
    
    