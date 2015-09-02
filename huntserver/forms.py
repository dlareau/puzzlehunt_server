from django import forms

class AnswerForm(forms.Form):
    answer = forms.CharField(max_length=100, label='Answer')

class SubmissionForm(forms.Form):
    response = forms.CharField(max_length=400, label='response', initial="Wrong Answer")
    sub_id = forms.CharField(label='sub_id')

class UnlockForm(forms.Form):
    team_id = forms.CharField(label='team_id')
    puzzle_id = forms.CharField(label='puzzle_id')

class RegistrationForm(forms.Form):
    team_name = forms.CharField(label='Team Name')
    username = forms.CharField(label='Team Username', required=False)
    password = forms.CharField(label='Team Password', widget=forms.PasswordInput())
    confirm_password = forms.CharField(label='Confirm Password', required=False, widget=forms.PasswordInput())
    first_name = forms.CharField(label='First Name')
    last_name =  forms.CharField(label='Last Name')
    phone = forms.CharField(label='Phone Number', required=False)
    email = forms.EmailField(label='Email')
    dietary_issues = forms.CharField(label='Dietary Restrictions?', required=False, widget = forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    year = forms.ChoiceField(label='School Year', choices=([(1,"Freshman"), (2,"Sophomore"), (3,"Junior"), (4,"Senior"), (5,"Graduate"), (0,"N/A")]))
    
    
