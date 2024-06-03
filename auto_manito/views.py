import random
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def home(request):
    return render(request, 'home.html')

@login_required
def manito_message(request):
    manito = request.user.manito
    return render(request, 'manito_message.html', {'manito': manito})

def get_users(request, group_id):
    users = Muser.objects.filter(group_id=group_id).values('id', 'username')
    return JsonResponse({'users': list(users)})

def assign_manito(users):
    random.shuffle(users)
    users_count = len(users)
    for i in range(users_count):
        users[i].manito = users[(i+1) % users_count]
        users[i].save()
