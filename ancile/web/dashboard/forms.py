from django import forms
from ancile.web.dashboard.models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class AdminAddPolicyForm(forms.Form):
    text = forms.CharField(label="Policy", widget=forms.Textarea)
    provider = forms.ChoiceField(label="Provider")
    active = forms.BooleanField(label="Active?", required=False)

    def __init__(self, *args, **kwargs):
        super(AdminAddPolicyForm, self).__init__(*args, **kwargs)
        app_choices = [(app.name, app.name) for app in App.objects.all()]
        self.fields['app'] = forms.ChoiceField(label="App", choices=app_choices)

class AdminEditPolicyForm(forms.Form):
    text = forms.CharField(label="Policy", widget=forms.Textarea)
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
        choices = [(scope.value, scope.simple_name) for scope in Scope.objects.all()]
        self.fields['scopes'] = forms.MultipleChoiceField(label="Scopes", choices=choices)

class AdminEditGroupForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")
    approved = forms.BooleanField(label="Approved?", required=False)

    def __init__(self, *args, **kwargs):
        super(AdminEditGroupForm, self).__init__(*args, **kwargs)
        choices = [(scope.value, scope.simple_name) for scope in Scope.objects.all()]
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
    text = forms.CharField(label="Policy", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(AdminAddPolicyTemplateForm, self).__init__(*args, **kwargs)
        provider_choices = [(provider.path_name, provider.display_name) for provider in DataProvider.objects.all()]
        self.fields['provider'] = forms.ChoiceField(label="Provider", choices=provider_choices)

class AdminEditPolicyTemplateForm(forms.Form):
    text = forms.CharField(label="Policy", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(AdminEditPolicyTemplateForm, self).__init__(*args, **kwargs)
        provider_choices = [(provider.path_name, provider.display_name) for provider in DataProvider.objects.all()]
        self.fields['provider'] = forms.ChoiceField(label="Provider", choices=provider_choices)

class AdminAddProviderForm(forms.Form):
    path_name = forms.CharField(label="Path Name")
    display_name = forms.CharField(label="Display Name")
    token_url = forms.CharField(label="Access Token URL")
    auth_url = forms.CharField(label="Authorize URL")
    client_id = forms.CharField(label="Client ID")
    client_secret = forms.CharField(label="Client Secret")
    json = forms.CharField(label="Extra Paramaters", widget=forms.Textarea)

class AdminAddScopeForm(forms.Form):
    simple_name = forms.CharField(label="Display Name")
    value = forms.CharField(label="Value")
    description = forms.CharField(label="Description")

class AdminEditScopeForm(AdminAddScopeForm):
    def __init__(self, *args, **kwargs):
        super(AdminEditScopeForm, self).__init__(*args, **kwargs)
        provider_choices = [(provider.path_name, provider.display_name) for provider in DataProvider.objects.all()]
        self.fields['provider'] = forms.ChoiceField(label="Provider", choices=provider_choices)

class DevEditAppForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")

    def __init__(self, *args, **kwargs):
        super(DevEditAppForm, self).__init__(*args, **kwargs)
        choices = [(user.username, user.username) for user in User.objects.all() if user.is_developer]
        self.fields['developers'] = forms.MultipleChoiceField(label="Developers", choices=choices)


class DevEditGroupForm(forms.Form):
    name = forms.CharField(label="Name")
    description = forms.CharField(label="Description")

    def __init__(self, *args, **kwargs):
        super(DevEditGroupForm, self).__init__(*args, **kwargs)
        choices = [(scope.value, scope.simple_name) for scope in Scope.objects.all()]
        self.fields['scopes'] = forms.MultipleChoiceField(label="Scopes", choices=choices)

class DevEditPolicyTemplateForm(forms.Form):
    text = forms.CharField(label="Policy", widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(DevEditPolicyTemplateForm, self).__init__(*args, **kwargs)
        provider_choices = [(provider.path_name, provider.display_name) for provider in DataProvider.objects.all()]
        self.fields['provider'] = forms.ChoiceField(label="Provider", choices=provider_choices)

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name", )

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            return username
        raise forms.ValidationError("Username already exists.")

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not email:
            raise forms.ValidationError("All fields are required.")
        try:
            get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return email
        raise forms.ValidationError("Email already exists.")

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"]
        if not first_name:
            raise forms.ValidationError("All fields are required.")

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"]
        if not last_name:
            raise forms.ValidationError("All fields are required.")

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
