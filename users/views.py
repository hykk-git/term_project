from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .forms import UserLoginForm
from .models import Muser, Mgroup
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import GroupRegistrationForm
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
import random

def assign_manito(users):
    random.shuffle(users)
    users_count = len(users)
    for i in range(users_count):
        users[i].manito = users[(i+1) % users_count]
        users[i].save()
        
def register_group(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        group_name = request.POST.get('group_name')
        
        if Mgroup.objects.filter(name=group_name).exists():
            # 그룹이 존재하면 오류 메시지를 반환합니다.
            return render(request, 'register_group.html', {'user_count': range(1, 6)}, {'error': '그룹이 이미 존재합니다. 다른 이름을 사용하세요.'})
        
        users_data = []

        # 기본 비밀번호 설정
        default_password = 'default_password'

        user_index = 1
        while request.POST.get(f'user_name{user_index}'):
            user_name = request.POST.get(f'user_name{user_index}')
            if user_name:
                users_data.append({
                    'user_name': user_name,
                    'password': make_password(default_password),
                })
            user_index += 1
            
        # 그룹 생성
        group, created = Mgroup.objects.get_or_create(name=group_name)
        
        # 사용자 생성
        users = []
        for user_data in users_data:
            user = Muser(username=user_data['user_name'], group=group, password=user_data['password'])
            user.save()
            users.append(user)
        
        #마니또 배정
        assign_manito(users)
        
        messages.success(request, '그룹과 구성원이 성공적으로 등록되었으며, 마니또가 할당되었습니다.')
        return redirect('success')  # 회원가입 성공 후 success 페이지로 리다이렉션

    return render(request, 'register_group.html', {'user_count': range(1, 6)})

def register_user(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        user_name = request.POST.get('user_name')
        new_password = request.POST.get('new_password')
        
        if not group_name or not user_name or not new_password:
            return render(request, 'register_user.html', {'error': '모든 필드를 입력하세요.', 'groups': Mgroup.objects.all()})
        
        group = Mgroup.objects.get(name=group_name)
        user = Muser.objects.get(username=user_name, group=group)

        user.password = make_password(new_password)
        user.save()

        messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
        return redirect('success')

    return render(request, 'register_user.html', {'groups': Mgroup.objects.all()})

def get_users(request):
    group_name = request.GET.get('group_name')
    group = Mgroup.objects.get(name=group_name)
    users = Muser.objects.filter(group=group).values('username')
    return JsonResponse(list(users), safe=False)

def user_login(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')

        if not group_name or not user_name or not password:
            return render(request, 'login.html', {'error': '모든 필드를 입력하세요.', 'groups': Mgroup.objects.all()})

        group = Mgroup.objects.get(name=group_name)
        user = authenticate(username=user_name, password=password)
        
        if user is not None and user.group == group:
            login(request, user)
            return redirect('manito_message')
        else:
            return render(request, 'login.html', {'error': '로그인 정보가 올바르지 않습니다.', 'groups': Mgroup.objects.all()})

    return render(request, 'login.html', {'groups': Mgroup.objects.all()})

def success(request):
    return render(request, 'success.html')

@login_required
def manito_message(request):
    user = request.user
    manito = user.manito
    context = {
        'manito_name': manito.username if manito else '마니또가 없습니다.'
    }
    return render(request, 'manito_message.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')