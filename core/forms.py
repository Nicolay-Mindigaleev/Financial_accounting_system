from django.contrib.auth.forms import UserCreationForm
from .models import UserData


class UserDataCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = UserData
        fields = ('username', 'password1', 'password2')
