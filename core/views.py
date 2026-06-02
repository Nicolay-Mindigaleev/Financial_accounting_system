from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Transaction, Category
from .forms import UserDataCreationForm
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from datetime import datetime


# registration and auntification
def register_view(request):
    if request.method == "POST":
        form = UserDataCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = UserDataCreationForm()
    return render(request, "core/registration.html",  {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
    else:
        form = AuthenticationForm()
    return render(request, "core/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("index")


# main page
@login_required
def index(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    categories = Category.objects.filter(user=request.user)
    now = datetime.now()
    transactions_for_last_month = Transaction.objects.filter(user=request.user,
                                                             date__year=now.year,
                                                             date__month=now.month)
    total_incomes = transactions_for_last_month.filter(operation="Income").aggregate(
        Sum("transaction_sum")
        )["transaction_sum__sum"] or 0
    total_expenses = transactions_for_last_month.filter(operation="Consumption").aggregate(
        Sum("transaction_sum")
        )["transaction_sum__sum"] or 0
    balance = total_incomes - total_expenses
    balance_sign = balance >= 0
    balance = abs(balance)
    main_total = {"incomes": total_incomes,
                  "expenses": total_expenses,
                  "balance": balance,
                  "balance_sign": balance_sign}
    return render(request, "core/index.html", {
        "transactions": transactions,
        "categories": categories,
        "transaction_sum": main_total
    })


# transaction CRUD
@login_required
def add_transaction(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == "POST":
        amount_str = request.POST.get("amount", "0")
        if not amount_str.isdigit() or float(amount_str) <= 0:
            return render(request, "core/add_transaction.html", {
                "categories": categories,
                "error": "Сумма операции должна быть положительным числом больше нуля."
            }, status=200)
        Transaction.objects.create(
            user=request.user,
            category_id=request.POST["category"],
            operation=request.POST["operation"],
            transaction_sum=request.POST["amount"],
            date=request.POST["date"],
            description=request.POST.get("description", "")
        )
        return redirect("index")
    return render(request, "core/add_transaction.html", {"categories": categories})


@login_required
def delete_transaction(request):
    transactions = Transaction.objects.filter(user=request.user)
    if request.method == "POST":
        transaction_id = request.POST.get("id")
        if transaction_id:
            Transaction.objects.filter(
                id=transaction_id,
                user=request.user
            ).delete()
        return redirect("index")
    return render(request, "core/delete_transaction.html", {"transactions": transactions})


@login_required
def change_transaction(request):
    transaction = Transaction.objects.filter(user=request.user).order_by('-date')
    categories = Category.objects.filter(user=request.user)
    if request.method == "POST":
        amount_str = request.POST.get("amount", "0")
        if not amount_str.isdigit() or float(amount_str) <= 0:
            return render(request, "core/add_transaction.html", {
                "categories": categories,
                "error": "Сумма операции должна быть положительным числом больше нуля."
            }, status=200)
        transaction_id = request.POST.get("transaction_id")
        transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
        transaction.category_id = request.POST["category"]
        transaction.operation = request.POST["operation"]
        transaction.transaction_sum = request.POST["amount"]
        transaction.date = request.POST["date"]
        transaction.description = request.POST.get("description", "")
        transaction.save()
        return redirect("index")
    return render(request, "core/change_transaction.html", {"transactions": transaction,
                                                            "categories": categories})


# categories CRUD
@login_required
def add_category(request):
    if request.method == "POST":
        category_name = request.POST.get("category_name", "").strip()
        if Category.objects.filter(user=request.user, category_name=category_name).exists():
            return render(request, "core/add_category.html", {
                "next_url": request.POST.get("next", ""),
                "error": f"Категория '{category_name}' уже существует."
            }, status=200)
        Category.objects.create(
            user=request.user,
            category_name=request.POST.get("category_name", "")
        )
        next_url = request.POST.get("next")
        if next_url:
            return redirect(next_url)
        return redirect("index")
    return render(request, "core/add_category.html", {"next_url": request.GET.get("next", "")})


@login_required
def delete_category(request):
    categories = Category.objects.filter(user=request.user)
    if request.method == "POST":
        category_id = request.POST.get("id")
        if category_id:
            Category.objects.filter(category_id=category_id,
                                    user=request.user).delete()
        return redirect("index")
    return render(request, "core/delete_category.html", {"categories": categories})


@login_required
def change_category(request):
    category_name = request.POST.get("category_name", "").strip()
    if Category.objects.filter(user=request.user, category_name=category_name).exists():
        return render(request, "core/add_category.html", {
            "next_url": request.POST.get("next", ""),
            "error": f"Категория '{category_name}' уже существует."
        }, status=200)
    categories = Category.objects.filter(user=request.user)
    if request.method == "POST":
        category_id = request.POST.get("id")
        new_name = request.POST.get("category_name", "").strip()
        if category_id and new_name:
            Category.objects.filter(category_id=category_id, user=request.user).update(category_name=new_name)
        return redirect("index")
    return render(request, "core/change_category.html", {"categories": categories})


# report page
@login_required
def report(request):
    from_date_str = request.GET.get('from')
    to_date_str = request.GET.get('to')
    sort_by = request.GET.get('sort', 'date')
    if from_date_str and to_date_str:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        transactions = Transaction.objects.filter(user=request.user, date__range=[from_date, to_date])
    else:
        now = datetime.now()
        from_date = datetime(now.year, now.month, 1).date()
        to_date = now.date()
        transactions = Transaction.objects.filter(user=request.user, date__range=[from_date, to_date])
    allowed_sort_fields = ['date', 'category__category_name', 'operation', 'transaction_sum', 'description']
    if sort_by.lstrip('-') in allowed_sort_fields:
        transactions = transactions.order_by(sort_by)
    else:
        transactions = transactions.order_by('date')
    total_incomes = transactions.filter(operation="Income").aggregate(
        Sum("transaction_sum")
        )["transaction_sum__sum"] or 0
    total_expenses = transactions.filter(operation="Consumption").aggregate(
        Sum("transaction_sum")
        )["transaction_sum__sum"] or 0
    balance = total_incomes - total_expenses
    balance_sign = balance >= 0
    balance = abs(balance)
    main_total = {"incomes": total_incomes,
                  "expenses": total_expenses,
                  "balance": balance,
                  "balance_sign": balance_sign}
    user_transactions = transactions
    category_expenses = (
        transactions.filter(operation="Consumption")
        .values("category__category_name")
        .annotate(total=Sum("transaction_sum"))
        .order_by("-total")
    )
    chart_labels = [item["category__category_name"] for item in category_expenses]
    chart_data = [float(item["total"]) for item in category_expenses]
    context = {
                "transaction": main_total,
                "from_date": from_date,
                "to_date": to_date,
                "transactions": user_transactions,
                "sort_by": sort_by,
                "chart_labels": chart_labels,
                "chart_data": chart_data,
            }
    return render(request, "core/report.html", context)
