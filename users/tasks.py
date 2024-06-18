from celery import shared_task
from django.utils import timezone
from .models import Mgroup, Muser, Message

@shared_task
def delete_expired_groups(group_id):
    now = timezone.now()
    try:
        group = Mgroup.objects.get(id=group_id, end_date__lt=now)
        Muser.objects.filter(group=group).delete()
        Message.objects.filter(sender__group=group).delete()
        Message.objects.filter(receiver__group=group).delete()
        group.delete()
    except Mgroup.DoesNotExist:
        pass  # 이미 삭제된 그룹일 경우 무시
