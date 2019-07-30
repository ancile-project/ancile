from django import forms
from ancile.web.dashboard.models import *

class AdminAddPolicyForm(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea)
    provider = forms.ChoiceField(label="Provider")
    app_list = App.objects.all()
    app_choices = [(app.name, app.name) for app in app_list]
    app = forms.ChoiceField(label="App", choices=app_choices)
    active = forms.BooleanField(label="Active?", required=False)

class AdminEditPolicyForm(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea)
    active = forms.BooleanField(label="Active?", required=False)

class AdminEditUserForm(forms.Form):
    app_list = App.objects.all()
    choices = [(app.name, app.name) for app in app_list]
    apps = forms.MultipleChoiceField(label="Developer For", required=False, choices=choices)
    is_admin = forms.BooleanField(label="Admin?", required=False)

