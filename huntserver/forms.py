from django import forms
from .models import Person
from django.conf import settings
from django.contrib.auth.models import User

class AnswerForm(forms.Form):
    answer = forms.CharField(max_length=100, label='Answer')

class SubmissionForm(forms.Form):
    response = forms.CharField(max_length=400, label='response', initial="Wrong Answer")
    sub_id = forms.CharField(label='sub_id')

class UnlockForm(forms.Form):
    team_id = forms.CharField(label='team_id')
    puzzle_id = forms.CharField(label='puzzle_id')

class PersonForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.fields['phone'].help_text = "Optional"

    allergies = forms.CharField(widget = forms.Textarea, label="Allergies", 
                                required=False, help_text="Optional")
    class Meta:
        model = Person
        fields = ['phone']

class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    required_css_class = 'required'
    confirm_password = forms.CharField(label='Confirm Password')
    class Meta:
        model = User 
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

class ShibUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShibUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['username'].help_text = "You can't change this, we need it for authentication"

    class Meta:
        model = User 
        fields = ['username', 'email', 'first_name', 'last_name']

class BaseRegisterForm(forms.Form):
    def save(self, attr):
        user = User.objects.create_user(attr[settings.SHIB_USERNAME], attr[settings.SHIB_EMAIL], '')
        return user
        