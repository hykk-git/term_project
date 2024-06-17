from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

def reassign_manito(collector, field, sub_objs, using):
    """
    This function is called when a 'manito' is deleted.
    It reassigns the deleted manito's manito to the user who had the deleted manito.
    """
    for obj in sub_objs:
        new_manito = obj.manito.manito if obj.manito else None
        obj.manito = new_manito
        obj.save()

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, group, username, password, **extra_fields):
        if not group:
            raise ValueError('The given group must be set')
        if not username:
            raise ValueError('The given username must be set')
        
        group_instance, created = Mgroup.objects.get_or_create(name=group)
        
        user = self.model(group=group_instance, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, group, username='', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(group, username, password, **extra_fields)

    def create_superuser(self, group, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(group, username, password, **extra_fields)

class Mgroup(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name
    
class Muser(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    group = models.ForeignKey(Mgroup, on_delete=models.CASCADE)
    manito = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    password = models.CharField(max_length=128)

    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["username", "group"],
                name="unique_username_per_group",
            )
        ]
        
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['group']

    def has_perm(self, perm, obj=None):
        return self.is_superuser or self.is_staff

    def has_module_perms(self, app_label):
        return self.is_superuser or self.is_staff

class Message(models.Model):
    sender = models.ForeignKey(Muser, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Muser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'From {self.sender.username} to {self.receiver.username}'
        
"""1. 등록시 그룹이름 겹칠때, 사용자 이름 겹칠 때 예외처리
    2. 비밀번호 틀렸을때
"""
