from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from . import constants


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class PlateSearchForm(forms.Form):
    # statestring = forms.ChoiceField(required=True, choices=constants.STATES, label='State or Territory')
    platetext = forms.CharField(label='License Plate (full or partial)', max_length=8)


class CommentForm(forms.Form):
    commenttext = forms.CharField(label='', max_length=140)
