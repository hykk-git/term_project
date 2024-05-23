from django.db import models
from django.contrib.auth.models import AbstractUser

def reassign_manito(collector, field, sub_objs, using):
    """
    This function is called when a 'manito' is deleted.
    It reassigns the deleted manito's manito to the user who had the deleted manito.
    """
    for obj in sub_objs:
        new_manito = obj.manito.manito  # Assuming 'manito' itself has a 'manito'.
        obj.manito = new_manito
        obj.save()

class Mgroup(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Muser(AbstractUser):
    username = models.CharField(max_length=150)
    group = models.ForeignKey(Mgroup, on_delete=models.CASCADE)
    manito = models.ForeignKey('self', on_delete=reassign_manito, null=True, blank=True)

    class Meta:
        unique_together = ('username', 'group')  # username과 group의 조합이 고유하도록 설정

    groups = models.ManyToManyField(
        'auth.Group',
        related_name="muser_groups"  # 각 Muser 인스턴스의 그룹 접근 시 사용할 이름
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="muser_permissions"  # 각 Muser 인스턴스의 권한 접근 시 사용할 이름
    )
