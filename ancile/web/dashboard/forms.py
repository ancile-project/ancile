from django import forms
from ancile.web.dashboard.models import *

class AdminAddPolicyForm(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea)
    provider = forms.ChoiceField(label="Provider")
    active = forms.BooleanField(label="Active?", required=False)

    def __init__(self, *args, **kwargs):
        super(AdminAddPolicyForm, self).__init__(*args, **kwargs)
        app_choices = [(app.name, app.name) for app in App.objects.all()]
        self.fields['app'] = forms.ChoiceField(label="App", choices=app_choices)

class AdminEditPolicyForm(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea)
    active = forms.BooleanField(label="Active?", required=False)

class AdminEditUserForm(forms.Form):
    is_admin = forms.BooleanField(label="Admin?", required=False)

    def __init__(self, *args, **kwargs):
        super(AdminEditUserForm, self).__init__(*args, **kwargs)
        choices = [(app.name, app.name) for app in App.objects.all()]
        self.fields['apps'] = forms.MultipleChoiceField(label="Developer For", required=False, choices=choices)

