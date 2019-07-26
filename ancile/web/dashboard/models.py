from urllib import parse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres import fields
from requests_oauthlib import OAuth2Session
from base64 import b64encode

class User(AbstractUser):
    pass


class App(models.Model):
    name = models.CharField(max_length=128, unique=True)
    developers = models.ManyToManyField(User)
    description = models.TextField()
    token_salt = models.CharField(max_length=64)
    salt_timestamp = models.TimeField()


class DataProvider(models.Model):
    name = models.CharField(max_length=128, unique=True)
    client_id = models.TextField()
    client_secret = models.TextField()
    access_token_url = models.TextField()
    auth_url = models.TextField()
    extra_params = fields.JSONField()

    @property
    def basic_auth_header(self):
        return str(b64encode(bytes(self.client_id + ":" + self.client_secret, 'utf8')), 'utf-8')

    def generate_url(self, scopes, base):
        session = OAuth2Session(
            client_id=self.client_id,
            redirect_uri=self.redirect_url(base),
            scope=scopes
        )

        auth_url, state = session.authorization_url(self.auth_url)
        return auth_url, state

    def redirect_url(self, base):
        return parse.urljoin(base, f"/oauth/{self.name}/callback")


class Policy(models.Model):
    text = models.TextField()
    provider = models.ForeignKey(DataProvider,
                                    null=True,
                                    on_delete=models.SET_NULL)
    user = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    app = models.ForeignKey(App,
                               on_delete=models.CASCADE)

    active = models.BooleanField()
    read_only = models.BooleanField()


class Scope(models.Model):
    name = models.TextField()
    provider = models.ForeignKey(DataProvider,
                                    on_delete=models.CASCADE)
    description = models.TextField(blank=True)


class PermissionGroup(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    app = models.ForeignKey(App,
                        on_delete=models.CASCADE)
    scopes = models.ManyToManyField(Scope)


class PredefinedPolicy(models.Model):
    provider = models.ForeignKey(DataProvider,
                                    null=True,
                                    on_delete=models.SET_NULL)
    app = models.ForeignKey(App,
                               on_delete=models.CASCADE)
    approved = models.BooleanField()
    group = models.ForeignKey(PermissionGroup,
                                 on_delete=models.CASCADE)

class Function(models.Model):
    name = models.CharField(max_length=128)
    body = models.TextField()
    app = models.ForeignKey(App,
                               on_delete=models.CASCADE)
    description = models.TextField()
    approved = models.BooleanField()

class Token(models.Model):
    user = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    provider = models.ForeignKey(DataProvider,
                                    on_delete=models.CASCADE)
    token_type = models.TextField()
    access_token = models.TextField()
    refresh_token = models.TextField(null=True)
    expires_at = models.IntegerField()
    scopes = models.ManyToManyField(Scope)


class PrivateData(models.Model):
    user = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    provider = models.ForeignKey(DataProvider,
                                    on_delete=models.CASCADE)
    value = fields.JSONField()
