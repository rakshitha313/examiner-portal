from django.shortcuts import render, redirect
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login, logout
from .forms import ExaminerUserForm, ExaminerForm
from .models import Examiner


def examiner_signup_view(request):
    userForm = ExaminerUserForm()
    examinerForm = ExaminerForm()

    if request.method == 'POST':
        userForm = ExaminerUserForm(request.POST)
        examinerForm = ExaminerForm(request.POST)

        if userForm.is_valid() and examinerForm.is_valid():
            username = userForm.cleaned_data.get('username')
            email = userForm.cleaned_data.get('email')
            phone = examinerForm.cleaned_data.get('phone')

            if User.objects.filter(username=username).exists():
                return render(request, 'examiner/signup.html', {
                    'userForm': userForm,
                    'examinerForm': examinerForm,
                    'error': 'Username already exists'
                })

            if User.objects.filter(email=email).exists():
                return render(request, 'examiner/signup.html', {
                    'userForm': userForm,
                    'examinerForm': examinerForm,
                    'error': 'Email already exists'
                })

            if Examiner.objects.filter(phone=phone).exists():
                return render(request, 'examiner/signup.html', {
                    'userForm': userForm,
                    'examinerForm': examinerForm,
                    'error': 'Phone number already exists'
                })

            user = userForm.save(commit=False)
            user.set_password(userForm.cleaned_data['password'])
            user.save()

            examiner = examinerForm.save(commit=False)
            examiner.user = user
            examiner.save()

            group, _ = Group.objects.get_or_create(name='EXAMINER')
            user.groups.add(group)

            login(request, user)
            return redirect('examiner-dashboard')

    return render(request, 'examiner/signup.html', {
        'userForm': userForm,
        'examinerForm': examinerForm
    })


def examiner_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.groups.filter(name='EXAMINER').exists():
            login(request, user)
            return redirect('examiner-dashboard')
        else:
            return render(request, 'examiner/login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'examiner/login.html')


def examiner_logout_view(request):
    logout(request)
    return redirect('examiner-login')

def examiner_welcome_view(request):
    return render(request, 'examiner/welcome.html')