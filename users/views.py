from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .forms import UserLoginForm
from .models import Muser, Mgroup
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import GroupRegistrationForm

def register(request):
    return redirect('register_user')

def register_group(request):
    if request.method == 'POST':
        form = GroupRegistrationForm(request.POST)
        if form.is_valid():
            group = form.save()
            members = [value for key, value in request.POST.items() if 'members' in key and value]
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
    return render(request, 'register_group.html', {'form': form, 'range': range(10)})

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