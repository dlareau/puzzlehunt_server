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
    class Meta:
        model = Person
        fields = ['phone', 'allergies']

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

class BaseRegisterForm(forms.Form):
    def save(self, attr):
        user = User.objects.create_user(attr[settings.SHIB_USERNAME], attr[settings.SHIB_EMAIL], '')
        return user
        
# class RegistrationForm(forms.Form):
#     team_name = forms.CharField(label='Team Name')
#     username = forms.CharField(label='Team Username', required=False)
#     password = forms.CharField(label='Team Password', widget=forms.PasswordInput())
#     confirm_password = forms.CharField(label='Confirm Password', required=False, widget=forms.PasswordInput())
#     location = forms.ChoiceField(label="Do you want to be provided a room on campus close to the hunt?", choices=([(1, "Yes"), (2, "No, we have a room"), (3, "No, we are a remote team")]), required=False) 
#     first_name = forms.CharField(label='First Name')
#     last_name =  forms.CharField(label='Last Name')
#     phone = forms.CharField(label='Phone Number', required=False)
#     email = forms.EmailField(label='Email')
#     dietary_issues = forms.CharField(label='Dietary Restrictions?', required=False, widget = forms.Textarea(attrs={'rows': 4, 'cols': 40}))
#     year = forms.ChoiceField(label='School Year', choices=([(1,"Freshman"), (2,"Sophomore"), (3,"Junior"), (4,"Senior"), (5,"Graduate"), (0,"N/A")]))
    
    
