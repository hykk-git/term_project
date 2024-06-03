from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Mgroup, Muser

class GroupRegistrationForm(UserCreationForm):
    members = forms.CharField(widget=forms.Textarea, help_text="Enter one username per line")

    class Meta:
        model = Mgroup
        fields = ['name']

    def save(self, commit=True):
        group = super().save(commit=commit)
        members = self.cleaned_data['members'].splitlines()
        for member_username in members:
            if member_username.strip():
                Muser.objects.create_user(username=member_username.strip(), password='defaultpassword', group=group)
        return group
    
class UserLoginForm(AuthenticationForm):
    group = forms.ModelChoiceField(queryset=Mgroup.objects.all(), required=True, label='Group')
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['password'].label = 'Password'