from urllib import parse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres import fields
from django.dispatch import receiver
from requests_oauthlib import OAuth2Session
from base64 import b64encode
from bcrypt import gensalt
from jwt import encode, decode
from config.loader import SECRET_KEY
import time
import requests
import json


class User(AbstractUser):
    is_developer = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    @property
    def apps(self):
        if self.is_developer:
            return App.objects.filter(developers=self)
        else:
            return []

    @property
    def tokens(self):
        return Token.objects.filter(user=self)

    def policies_for_app(self, app):
        return Policy.objects.filter(app=app, user=self, active=True)


class AppManager(models.Manager):
    def retrieve_app_id(self, coded_salt):
        token_salt = decode(coded_salt, SECRET_KEY)["salt"]
        return self.filter(token_salt=token_salt).values('id')[0]['id']


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
    path_name = models.CharField(max_length=128, unique=True)
    display_name = models.TextField(unique=True, blank=True)
    client_id = models.TextField()
    client_secret = models.TextField()
    access_token_url = models.TextField()
    auth_url = models.TextField()
    extra_params = fields.JSONField(default=dict)

    @property
    def request_headers(self):
        basic_header = str(
            b64encode(bytes(self.client_id + ":" + self.client_secret, "utf8")), "utf-8"
        )
        return {"Authorization": "basic " + basic_header}

    def generate_url(self, scopes, base):
        session = OAuth2Session(
            client_id=self.client_id, redirect_uri=self.redirect_url(base), scope=scopes
        )

        extra_params = json.loads(self.extra_params) \
            if isinstance(self.extra_params, str) else self.extra_params

        auth_url, state = session.authorization_url(self.auth_url, **extra_params)
        return auth_url, state

    def redirect_url(self, base):
        return parse.urljoin(base, f"/oauth/{self.path_name}/callback")


@receiver(models.signals.post_init, sender=DataProvider)
def set_display_name(sender, instance, *args, **kwargs):
    if not instance.display_name:
        instance.display_name = instance.path_name.capitalize()


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

    @property
    def policies(self):
        return PolicyTemplate.objects.filter(group=self)


class PolicyTemplate(models.Model):
    provider = models.ForeignKey(DataProvider, null=True, on_delete=models.SET_NULL)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    group = models.ForeignKey(PermissionGroup, on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        verbose_name = "Policy Template"
        verbose_name_plural = "Policy Templates"


class FunctionManager(models.Manager):
    def get_app_module(self, app_id):
        return "\n\n".join((fn.body for fn in self.filter(app_id=app_id)))


class Function(models.Model):
    name = models.CharField(max_length=128)
    body = models.TextField()
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    description = models.TextField()
    approved = models.BooleanField(default=False)

    objects = FunctionManager()


class TokenManager(models.Manager):
    def create_token(self, user, provider, response):
        token = Token(user=user, provider=provider)
        token._update_token(response)
        return token


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

    objects = TokenManager()

    @property
    def expired(self):
        return time.time() >= self.expires_at

    def _update_token(self, update_dict):
        self.token_type = update_dict.get("token_type", self.token_type)
        self.access_token = update_dict.get("access_token", self.access_token)
        self.refresh_token = update_dict.get("refresh_token", self.refresh_token)

        expires_in = update_dict.get("expires_in", False)
        if expires_in:
            self.expires_at = time.time() + expires_in

        self.save()

        self.scopes.clear()

        scopes_raw = update_dict.get("scope")
        scopes = scopes_raw.split() if scopes_raw else []

        for scope in scopes:
            try:
                scope_object = Scope.objects.get(
                    value=scope, provider=self.provider
                )
            except Scope.DoesNotExist:
                scope_object = Scope(
                    value=scope, provider=self.provider, description=""
                )
                scope_object.save()
            finally:
                self.scopes.add(scope_object)

    def refresh(self):
        if self.refresh_token:
            request_body = {
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token",
                "client_id": self.provider.client_id,
                "client_secret": self.provider.client_secret,
            }

            response = requests.post(
                self.provider.access_token_url,
                headers=self.provider.request_headers,
                data=request_body,
            )

            if response.status_code == 200:
                self._update_token(response.json())
                return True
            else:
                return False


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

class PendingDeveloper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
