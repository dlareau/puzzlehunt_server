from django import forms
from .models import Person
from django.contrib.auth.models import User
import re


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
        self.fields['allergies'].help_text = "Optional"
        self.fields['allergies'].label = "Allergies"

    class Meta:
        model = Person
        fields = ['phone', 'allergies']


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['password'].widget = forms.PasswordInput()

    required_css_class = 'required'
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Someone is already using that email address.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if(re.match("^[a-zA-Z0-9]+([_-]?[a-zA-Z0-9])*$", username) is None):
            raise forms.ValidationError("Username must contain only letters, digits, or '-' or '_'")
        return username

    def clean_confirm_password(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')
        if password1 and password2 and (password1 == password2):
            return password1
        else:
            raise forms.ValidationError('Passwords must match')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        help_texts = {
            'username': "Required. 30 characters or fewer. Letters, digits and '-' or '_' only.",
        }


class ShibUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ShibUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['username'].help_text = "You can't change this, we need it for authentication"

    def clean_username(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            return instance.username
        else:
            return self.cleaned_data['username']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Someone is already using that email address.')
        return email

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class EmailForm(forms.Form):
    subject = forms.CharField(label='Subject')
    message = forms.CharField(label='Message', widget=forms.Textarea)


class HintRequestForm(forms.Form):
    request = forms.CharField(max_length=400, label='Hint Request Text', widget=forms.Textarea,
                              help_text="Please describe your progress on the puzzle, and where "
                                        "you feel you are stuck. Max length 400 characters.")


class HintResponseForm(forms.Form):
    response = forms.CharField(max_length=400, label='Hint Response Text',
                               widget=forms.Textarea(attrs={'rows': 5, 'cols': 30}),
                               help_text="Max length 400 characters.")
    hint_id = forms.CharField(label='hint_id', widget=forms.HiddenInput())
