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
    is_developer = forms.BooleanField(label="Developer?", required=False)
    is_admin = forms.BooleanField(label="Admin?", required=False)

    def __init__(self, *args, **kwargs):
        super(AdminEditUserForm, self).__init__(*args, **kwargs)
        choices = [(app.name, app.name) for app in App.objects.all()]
        self.fields['apps'] = forms.MultipleChoiceField(label="Developer For", required=False, choices=choices)

class AdminEditAppForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")

    def __init__(self, *args, **kwargs):
        super(AdminEditAppForm, self).__init__(*args, **kwargs)
        choices = [(user.username, user.username) for user in User.objects.all()]
        self.fields['developers'] = forms.MultipleChoiceField(label="Developers", choices=choices)

class AdminAddGroupForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")
    approved = forms.BooleanField(label="Approved?", required=False)

    def __init__(self, *args, **kwargs):
        super(AdminAddGroupForm, self).__init__(*args, **kwargs)
        choices = [(scope.value, scope.value) for scope in Scope.objects.all()]
        self.fields['scopes'] = forms.MultipleChoiceField(label="Scopes", choices=choices)

class AdminEditGroupForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")
    approved = forms.BooleanField(label="Approved?", required=False)

    def __init__(self, *args, **kwargs):
        super(AdminEditGroupForm, self).__init__(*args, **kwargs)
        choices = [(scope.value, scope.value) for scope in Scope.objects.all()]
        self.fields['scopes'] = forms.MultipleChoiceField(label="Scopes", choices=choices)

class AdminAddFunctionForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")
    approved = forms.BooleanField(label="Approved?", required=False)
    body = forms.CharField(label="Code", widget=forms.Textarea)

class AdminEditFunctionForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")
    approved = forms.BooleanField(label="Approved?", required=False)
    body = forms.CharField(label="Code", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(AdminEditFunctionForm, self).__init__(*args, **kwargs)
        choices = [(app.id, app.name) for app in App.objects.all()]
        self.fields['app_id'] = forms.ChoiceField(label="App", choices=choices)

class AdminAddPolicyTemplateForm(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(AdminAddPolicyTemplateForm, self).__init__(*args, **kwargs)
        provider_choices = [(provider.path_name, provider.display_name) for provider in DataProvider.objects.all()]
        self.fields['provider'] = forms.ChoiceField(label="Provider", choices=provider_choices)

class AdminEditPolicyTemplateForm(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(AdminEditPolicyTemplateForm, self).__init__(*args, **kwargs)
        provider_choices = [(provider.path_name, provider.display_name) for provider in DataProvider.objects.all()]
        self.fields['provider'] = forms.ChoiceField(label="Provider", choices=provider_choices)
