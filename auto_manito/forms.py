from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Muser, Mgroup
import logging

logger = logging.getLogger(__name__)
class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    group = forms.ModelChoiceField(queryset=Mgroup.objects.all())

    def __init__(self, *args, **kwargs):
        group_id = kwargs.pop('group_id', None)
        super().__init__(*args, **kwargs)
        if group_id:
            self.fields['username'].queryset = Muser.objects.filter(group_id=group_id)
        else:
            self.fields['username'].queryset = Muser.objects.none()


class GroupRegistrationForm(forms.ModelForm):
    class Meta:
        model = Mgroup
        fields = ['name']

logger = logging.getLogger(__name__)

class UserLoginForm(AuthenticationForm):
    group = forms.ModelChoiceField(queryset=Mgroup.objects.all(), required=True, label='Group')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['password'].label = 'Password'

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        group = cleaned_data.get('group')

        # 디버깅 출력
        print(f'Login attempt: Username={username}, Password={password}, Group={group}')

        if username and password and group:
            try:
                user = Muser.objects.get(username=username, group=group)
                if user.check_password(password):
                    print(f'Password check success for user {username} in group {group}')
                else:
                    print(f'Password check failed for user {username} in group {group}')
                    raise forms.ValidationError('Please enter a correct username and password. Note that both fields may be case-sensitive.')
            except Muser.DoesNotExist:
                print(f'User {username} does not exist in group {group}')
                raise forms.ValidationError('Please enter a correct username and password. Note that both fields may be case-sensitive.')
        else:
            print('Form is missing username, password, or group')
        return cleaned_data