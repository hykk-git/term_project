import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .models import Muser, Mgroup
from .forms import UserLoginForm, UserRegistrationForm, GroupRegistrationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'home.html')

def register(request):
    return redirect('register_user')

def register_group(request):
    if request.method == 'POST':
        form = GroupRegistrationForm(request.POST)
        if form.is_valid():
            group = form.save()
            members = [value for key, value in request.POST.items() if 'member' in key and value]
            users = []
            for member_username in members:
                if Muser.objects.filter(username=member_username, group=group).exists():
                    messages.error(request, f"사용자 이름 '{member_username}'가 이미 그룹 '{group.name}'에 존재합니다.")
                    return redirect('register_group')
                user = Muser.objects.create_user(username=member_username, password='defaultpassword', group=group)
                user.set_password('defaultpassword')  # 비밀번호 해싱
                user.save()
                users.append(user)
            
            random.shuffle(users)
            users_count = len(users)
            for i in range(users_count):
                users[i].manito = users[(i+1) % users_count]
                users[i].save()

            messages.success(request, '그룹과 구성원이 성공적으로 등록되었으며, 마니또가 할당되었습니다.')
            return redirect('success')
        else:
            messages.error(request, '입력 정보를 확인하세요.')
    else:
        form = GroupRegistrationForm()
    return render(request, 'register_group.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                user = Muser.objects.get(username=username, group=group)
                user.set_password(password)  # 비밀번호 해싱
                user.save()
                messages.success(request, '사용자가 성공적으로 등록되었습니다.')
                logger.info(f"User {username} in group {group.name} password updated.")
                return redirect('success')
            except Muser.DoesNotExist:
                messages.error(request, f"사용자 이름 '{username}'가 이미 그룹 '{group.name}'에 존재하지 않습니다.")
                logger.error(f"User {username} in group {group.name} does not exist.")
        else:
            messages.error(request, '입력 정보를 확인하세요.')
    else:
        form = UserRegistrationForm()
    return render(request, 'register_user.html', {'form': form})

class CustomLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'login.html'

    def form_valid(self, form):
        print("form_valid called")
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        group = form.cleaned_data.get('group')

        print(f"Form valid method called with username={username}, password={password}, group={group}")

        try:
            user = Muser.objects.get(username=username, group=group)
            if user.check_password(password):
                print(f"User {username} authenticated successfully")
                login(self.request, user)
                return redirect('manito_message')
            else:
                print(f"Password check failed for user {username} in group {group}")
                form.add_error('password', '비밀번호가 잘못되었습니다.')
        except Muser.DoesNotExist:
            print(f"User {username} does not exist in group {group}")
            form.add_error('username', '해당 사용자가 존재하지 않습니다.')

        return self.form_invalid(form)

    def form_invalid(self, form):
        print(f"Form invalid: {form.errors.as_json()}")
        return super().form_invalid(form)

    def get_success_url(self):
        return self.get_redirect_url() or 'manito_message'
    
@login_required
def assign_manito(request):
    group = request.user.group
    users = list(group.muser_set.all())
    random.shuffle(users)
    users_count = len(users)
    for i in range(users_count):
        users[i].manito = users[(i+1) % users_count]
        users[i].save()
    return redirect('check_manito')

@login_required
def check_manito(request):
    manito = request.user.manito
    return render(request, 'check_manito.html', {'manito': manito})

@login_required
def manito_message(request):
    manito = request.user.manito
    return render(request, 'manito_message.html', {'manito': manito})

def success(request):
    return render(request, 'success.html')

def get_users(request, group_id):
    users = Muser.objects.filter(group_id=group_id).values('id', 'username')
    return JsonResponse({'users': list(users)})
