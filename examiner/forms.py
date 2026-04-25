from django import forms
from django.contrib.auth.models import User
from .models import Examiner


class ExaminerUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']


class ExaminerForm(forms.ModelForm):
    class Meta:
        model = Examiner
        fields = ['phone', 'organization']