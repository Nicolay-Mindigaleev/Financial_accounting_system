from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Transaction, Category
from .forms import UserDataCreationForm
#registration or auntification

def register_view(request):
    if request.method == "POST":
        form = UserDataCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("index")
    form = UserDataCreationForm()
    return render(request, "core/registration.html",  {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("index")
    form = AuthenticationForm()
    return render(request, "core/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("index")

#main functional

@login_required
def index(request):
    transactions = Transaction.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)
    return render(request, "core/index.html", {
        "transactions": transactions,
        "categories": categories
    })

@login_required
def add_transaction(request):
    if request.method == "POST":
        Transaction.objects.create(
            user=request.user,
            category_id=request.POST["category"],
            operation=request.POST["operation"],
            transaction_sum=request.POST["amount"],
            date=request.POST["date"],
            description=request.POST.get("description", "")
        )
    return redirect("index")

@login_required
def delete_transaction(request):
    if request.method == "POST":
        transaction_id = request.POST.get("id")
        if transaction_id:
            Transaction.objects.filter(
                id=transaction_id,
                user=request.user
            ).delete()
    return redirect("index")

@login_required
def change_transaction(request):
    if request.method == "POST":
        transaction_id = request.POST.get("id")
        if transaction_id:
            Transaction.objects.filter(
                    id=transaction_id,
                    user=request.user
            ).update(
                category_id=request.POST["category"],
                operation=request.POST["operation"],
                transaction_sum=request.POST["amount"],
                date=request.POST["date"],
                description=request.POST.get("description", "")               
            )
    return redirect("index")