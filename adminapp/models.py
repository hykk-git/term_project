from django.db import models
from users.models import Muser, Mgroup

class Announcement(models.Model):
    manager = models.ForeignKey(Muser, on_delete=models.CASCADE, related_name='announcements')
    group = models.ForeignKey(Mgroup, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    target_user = models.ForeignKey('users.Muser', null=True, blank=True, on_delete=models.CASCADE, related_name='target_announcements')

    def __str__(self):
        return f'Announcement by {self.manager.username}'