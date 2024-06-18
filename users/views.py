from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from .models import Muser, Mgroup, Message
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.urls import reverse
from django.middleware.csrf import get_token
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.utils import timezone
import json
import random

def assign_manito(users):
    random.shuffle(users)
    users_count = len(users)
    for i in range(users_count):
        users[i].manito = users[(i+1) % users_count]
        users[i].save()
        
def register_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        end_date = request.POST.get('end_date')
        
        end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%dT%H:%M'))
        
        if Mgroup.objects.filter(name=group_name).exists():
            # 그룹이 존재하면 오류 메시지를 반환
            return render(request, 'register_group.html', {'user_count': range(1, 6), 'error': '그룹이 이미 존재합니다. 다른 이름을 사용하세요.'})
        
        users_data = []
        existing_usernames = []
        duplicate_usernames = []

        # 기본 비밀번호 설정
        default_password = 'default_password'

        user_index = 1
        while request.POST.get(f'username{user_index}'):
            username = request.POST.get(f'username{user_index}')
            if username:
                if Muser.objects.filter(username=username).exists():
                    duplicate_usernames.append(username)
                else:
                    users_data.append({
                        'username': username,
                        'password': make_password(default_password),
                    })
                    existing_usernames.append(username)
            user_index += 1
            
        if duplicate_usernames:
            error_message = f"다음 사용자 이름은 이미 존재합니다: {', '.join(duplicate_usernames)}"
            return render(request, 'register_group.html', {'user_count': range(1, 6), 'error': error_message})
        
        # 그룹 생성
        group, created = Mgroup.objects.get_or_create(name=group_name, end_date=end_date)
        
        # 사용자 생성
        users = []
        for user_data in users_data:
            user = Muser(username=user_data['username'], group=group, password=user_data['password'])
            user.save()
            users.append(user)
        
        # 마니또 배정
        assign_manito(users)
        
        # 주기적인 작업 생성
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='0',
            day_of_month='*',
            month_of_year='*',
            day_of_week='*'
        )

        PeriodicTask.objects.create(
            crontab=schedule,
            name=f'Delete expired group {group_name}',
            task='users.tasks.delete_expired_groups',
            args=json.dumps([group.id]),
            expires=end_date  # 작업 만료일을 그룹 종료일로 설정
        )

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

        messages.success(request, '비밀키가 설정되었습니다.')
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

        try:
            group = Mgroup.objects.get(name=group_name)
        except Mgroup.DoesNotExist:
            return render(request, 'login.html', {'error': '존재하지 않는 그룹입니다.', 'groups': Mgroup.objects.all()})

        user = authenticate(request, username=user_name, password=password)

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
    end_date = user.group.end_date if user.group.end_date else None
    context = {
        'manito_name': manito.username if manito else '마니또가 없습니다.',
        'end_date' : end_date.strftime('%Y-%m-%d %H:%M:%S') if end_date else "0"
    }
    return render(request, 'manito_message.html', context)

@login_required
def send_message(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if not content or len(content) > 50:
            return JsonResponse({'error': 'Invalid message content'}, status=400)

        sender = request.user
        receiver = sender.manito

        if not receiver:
            return JsonResponse({'error': 'No manito assigned'}, status=400)

        if Message.objects.filter(receiver=receiver).count() >= 5:
            return JsonResponse({'error': 'Receiver\'s inbox is full'}, status=400)

        message = Message(sender=sender, receiver=receiver, content=content)
        message.save()

        return JsonResponse({'success': 'Message sent successfully'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def inbox(request):
    user = request.user
    messages = Message.objects.filter(receiver=user)
    messages_data = [{'id': message.id, 'content': message.content} for message in messages]
    csrf_token = get_token(request)
    return JsonResponse({'messages': messages_data, 'csrf_token': csrf_token})

@login_required
def delete_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id, receiver=request.user)
        message.delete()
        return redirect('inbox')
    except Message.DoesNotExist:
        return redirect('inbox')
    
def logout_view(request):
    logout(request)
    return redirect(reverse('home'))