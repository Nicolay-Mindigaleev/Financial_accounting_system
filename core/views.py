from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Transaction
from .forms import UserDataCreationForm
#registration or auntification

def register_view(request):
    if request.method == "POST":
        form = UserDataCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("index")
    form = UserDataCreationForm()
    return render(request, "core/registration.html",  {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
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
    return render(request, "core/index.html", {'transactions': transactions})
def add_transaction(request):
    return redirect("index")