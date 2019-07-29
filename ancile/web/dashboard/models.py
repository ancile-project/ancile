from urllib import parse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres import fields
from requests_oauthlib import OAuth2Session
from base64 import b64encode
from bcrypt import gensalt


class User(AbstractUser):
    is_developer = models.BooleanField(default=False)

    @property
    def apps(self):
        if self.is_developer:
            return App.objects.filter(developers=self).all()
        else:
            return []

class App(models.Model):
    name = models.CharField(max_length=128, unique=True)
    developers = models.ManyToManyField(User)
    description = models.TextField()
    token_salt = models.CharField(max_length=64, unique=True, default=gensalt)
    salt_timestamp = models.TimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"


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


class Scope(models.Model):
    name = models.TextField()
    provider = models.ForeignKey(DataProvider, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "provider"], name="scope:unique_scope_provider"
            )
        ]


class PermissionGroup(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    scopes = models.ManyToManyField(Scope)


class PredefinedPolicy(models.Model):
    provider = models.ForeignKey(DataProvider, null=True, on_delete=models.SET_NULL)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    approved = models.BooleanField()
    group = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Predefined policy"
        verbose_name_plural = "Predefined policies"


class Function(models.Model):
    name = models.CharField(max_length=128)
    body = models.TextField()
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    description = models.TextField()
    approved = models.BooleanField(default=False)


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
