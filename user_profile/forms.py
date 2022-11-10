from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name',
            'email', 'password1', 'password2',)


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('about_me', 'avatar', 'favorite_location')
        widgets = {
            'favorite_location': forms.Select(attrs={'class': 'form-control'}),
            # 'avatar': forms.Input(attrs={'class': 'form-control'}),
        }


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',)
