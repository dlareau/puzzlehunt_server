from django import forms

class AnswerForm(forms.Form):
    answer = forms.CharField(max_length=100, label='Answer')
