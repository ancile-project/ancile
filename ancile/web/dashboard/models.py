from urllib import parse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres import fields
from requests_oauthlib import OAuth2Session
from base64 import b64encode
from bcrypt import gensalt
from jwt import encode, decode
from config.loader import SECRET_KEY


class User(AbstractUser):
    is_developer = models.BooleanField(default=False)

    @property
    def apps(self):
        if self.is_developer:
            return App.objects.filter(developers=self).all()
        else:
            return []

    def policies_for_app(self, app):
        return Policy.objects.filter(app=app, user=self, active=True).all()


class AppManager(models.Manager):
    def retrieve_app(self, coded_salt):
        token_salt = decode(coded_salt, SECRET_KEY)["salt"]
        return self.get(token_salt=token_salt)


class App(models.Model):
    name = models.CharField(max_length=128, unique=True)
    developers = models.ManyToManyField(User)
    description = models.TextField()
    token_salt = models.CharField(max_length=64, unique=True, default=gensalt)
    salt_timestamp = models.TimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    objects = AppManager()

    @property
    def encoded_salt(self):
        return encode({"salt": self.token_salt}, SECRET_KEY).decode("ascii")


class DataProvider(models.Model):
    name = models.CharField(max_length=128, unique=True)
    client_id = models.TextField()
    client_secret = models.TextField()
    access_token_url = models.TextField()
    auth_url = models.TextField()
    extra_params = fields.JSONField(default=dict)

    @property
    def basic_auth_header(self):
        return str(
            b64encode(bytes(self.client_id + ":" + self.client_secret, "utf8")), "utf-8"
        )

    def generate_url(self, scopes, base):
        session = OAuth2Session(
            client_id=self.client_id, redirect_uri=self.redirect_url(base), scope=scopes
        )

        auth_url, state = session.authorization_url(self.auth_url)
        return auth_url, state

    def redirect_url(self, base):
        return parse.urljoin(base, f"/oauth/{self.name}/callback")


class Policy(models.Model):
    text = models.TextField()
    provider = models.ForeignKey(DataProvider, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app = models.ForeignKey(App, on_delete=models.CASCADE)

    active = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Policy"
        verbose_name_plural = "Policies"
        indexes = [models.Index(fields=["user", "app"])]


class Scope(models.Model):
    value = models.TextField()
    simple_name = models.TextField()
    provider = models.ForeignKey(DataProvider, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["value", "provider"], name="scope:unique_scope_provider"
            )
        ]


class PermissionGroup(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    scopes = models.ManyToManyField(Scope)
    approved = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "app"], name="permission_group:unique_name_app"
            )
        ]

    @property
    def provider_scope_list(self):
        provider_dict = dict()

        for scope in self.scopes.all():
            if scope.provider in provider_dict:
                provider_dict[scope.provider].append(scope)
            else:
                provider_dict[scope.provider] = [scope]

        return [(prov, scopes) for prov, scopes in provider_dict.items()]


class PredefinedPolicy(models.Model):
    provider = models.ForeignKey(DataProvider, null=True, on_delete=models.SET_NULL)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    group = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Predefined policy"
        verbose_name_plural = "Predefined policies"


class FunctionManager(models.Manager):
    def get_app_module(self, app):
        return "\n\n".join((fn.body for fn in self.filter(app=app).all()))


class Function(models.Model):
    name = models.CharField(max_length=128)
    body = models.TextField()
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    description = models.TextField()
    approved = models.BooleanField(default=False)

    objects = FunctionManager()


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(DataProvider, on_delete=models.CASCADE)
    token_type = models.TextField()
    access_token = models.TextField()
    refresh_token = models.TextField(null=True)
    expires_at = models.IntegerField()
    scopes = models.ManyToManyField(Scope)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "provider"], name="token:unique_user_provider"
            )
        ]


class PrivateData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(DataProvider, on_delete=models.CASCADE)
    value = fields.JSONField(default=dict)

    class Meta:
        verbose_name = "Private data"
        verbose_name_plural = "Private data"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "provider"], name="private_data:unique_user_provider"
            )
        ]
