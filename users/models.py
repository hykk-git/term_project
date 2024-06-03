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
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Muser(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    group = models.ForeignKey(Mgroup, on_delete=models.CASCADE)
    manito = models.ForeignKey('self', on_delete=reassign_manito, null=True, blank=True)
    password = models.CharField(max_length=255)
    class Meta:
        unique_together = ('username', 'group')  # username과 group의 조합이 고유하도록 설정
    
    USERNAME_FIELD = 'username' 
    def has_perm(self, perm, obj=None):
    	return True
        
    def has_module_perms(self, app_label):
        return True 