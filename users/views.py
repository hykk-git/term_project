from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .forms import UserLoginForm
from .models import Muser, Mgroup
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import GroupRegistrationForm
from django.contrib.auth.hashers import make_password

def register(request):
    return redirect('register_user')

def register_group(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        group = request.POST.get('group')
        if Mgroup.objects.filter(name=group).exists():
            # 그룹이 존재하면 오류 메시지를 반환합니다.
            return render(request, 'register_group.html', {'user_count': range(1, 6)}, {'error': '그룹이 이미 존재합니다. 다른 이름을 사용하세요.'})
        
        users_data = []

        # 기본 비밀번호 설정
        default_password = 'default_password'

        user_index = 1
        while request.POST.get(f'username{user_index}'):
            username = request.POST.get(f'username{user_index}')
            if username:
                users_data.append({
                    'username': username,
                    'password': make_password(default_password),
                })
            user_index += 1
            
        # 그룹 생성
        group, created = Mgroup.objects.get_or_create(name=group)
        
        # 사용자 생성
        for user_data in users_data:
            Muser.objects.create(username=user_data['username'], group=group, password=user_data['password'])
        messages.success(request, '그룹과 구성원이 성공적으로 등록되었으며, 마니또가 할당되었습니다.')
        return redirect('success')  # 회원가입 성공 후 success 페이지로 리다이렉션

    return render(request, 'register_group.html', {'user_count': range(1, 6)})

def register_user(request):
    if request.method == 'POST':
        password = request.POST["password"]
        try:
            user = Muser.objects.get(username=username, group=group)
            user.set_password(password)  # 비밀번호 해싱
            user.save()
            messages.success(request, '사용자의 비밀번호가 성공적으로 업데이트되었습니다.')
        except Muser.DoesNotExist:
            user = Muser(username=username, group=group)
            user.set_password(password)  # 비밀번호 해싱
            user.save()
            messages.success(request, '사용자가 성공적으로 등록되었습니다.')
        return redirect('success')
    else:
        messages.error(request, '입력 정보를 확인하세요.')

    return render(request, 'register_user.html')

def login(request):
    groups = Mgroup.objects.all()
    if request.method == 'POST':
        login_form = UserLoginForm(request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            group = login_form.cleaned_data.get('group')
            print(password)
            try:
                user = Muser.objects.get(username=username, group=group)
                if user.check_password(password):
                    auth_login(request, user)
                    return redirect('manito_message')
                else:
                    login_form.add_error('password', '비밀번호가 잘못되었습니다.')
            except Muser.DoesNotExist:
                login_form.add_error('username', '해당 사용자가 존재하지 않습니다.')
        else:
            messages.error(request, '로그인 정보가 잘못되었습니다.')
    else:
        login_form = UserLoginForm()
    
    return render(request, 'login.html', {'login_form': login_form, 'groups': groups})

def success(request):
    return render(request, 'success.html')

@login_required
def check_manito(request):
    manito = request.user.manito
    return render(request, 'check_manito.html', {'manito': manito})

def manito_message(request):
    manito = request.user.manito
    return render(request, 'manito_message.html', {'manito': manito})

def get_users(request, group_id):
    users = Muser.objects.filter(group_id=group_id).values('id', 'username')
    return JsonResponse({'users': list(users)})