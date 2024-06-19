# adminapp/views.py

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Announcement
from users.models import Mgroup, Muser
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

def manager_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            manager = Muser.objects.get(username=username, is_manager=True)
            if manager.check_password(password):
                login(request, manager)
                return redirect('manager_dashboard')
            else:
                messages.error(request, '잘못된 비밀번호입니다.')
        except Muser.DoesNotExist:
            messages.error(request, '존재하지 않는 관리자입니다.')

    return render(request, 'manager_login.html')

@login_required
def manager_dashboard(request):
    if not request.user.is_manager:
        return redirect('home')

    group = request.user.group
    if request.method == 'POST':
        content = request.POST.get('content')
        target_user_id = request.POST.get('target_user')
        if content:
            if target_user_id:
                target_user = Muser.objects.get(id=target_user_id)
                Announcement.objects.create(manager=request.user, group=group, content=content, target_user=target_user)
            else:
                Announcement.objects.create(manager=request.user, group=group, content=content)
                return JsonResponse({'success': '공지사항을 보냈습니다.'})

    users = Muser.objects.filter(group=group).exclude(id=request.user.id)
    announcements = Announcement.objects.filter(group=group).order_by('-created_at')[:10]
    context = {
        'group_name': group.name,
        'users': users,
        'announcements': announcements
    }
    return render(request, 'manager_dashboard.html', context)

@login_required
def delete_group(request):
    if not request.user.is_manager:
        return redirect('home')

    group = request.user.group
    group.delete()
    return JsonResponse({'success': '그룹이 성공적으로 삭제되었습니다.'})

@login_required
def delete_announcement(request, announcement_id):
    if not request.user.is_manager:
        return redirect('home')
    
    announcement = get_object_or_404(Announcement, id=announcement_id, group=request.user.group)
    announcement.delete()
