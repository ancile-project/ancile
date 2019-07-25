from urllib import parse
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres import fields
import requests_oauthlib

class User(AbstractUser):
    pass


class App(models.Model):
    name = models.CharField(max_length=128, unique=True)
    developer_ids = models.ManyToManyField(User)
    description = models.TextField()
    token_salt = models.CharField(max_length=64)
    salt_timestamp = models.TimeField()


class DataProvider(models.Model):
    name = models.CharField(max_length=128, unique=True)
    client_id = models.TextField()
    client_secret = models.TextField()
    base_url = models.TextField()
    access_token_url = models.TextField()
    auth_url = models.TextField()
    extra_params = fields.JSONField()

    def generate_url(self, scopes, base):
        session = requests-oauthlib.OAuth2Session(
            client_id=self.client_id,
            redirect_url=redirect_url(base)
        )

        auth_url, state = session.authorization_url(self.auth_url)
        return auth_url, state

    def redirect_url(self, base):
        return parse.urljoin(base, f"/{self.name}/callback")


class Policy(models.Model):
    text = models.TextField()
    provider_id = models.ForeignKey(DataProvider,
                                    null=True,
                                    on_delete=models.SET_NULL)
    user_id = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    app_id = models.ForeignKey(App,
                               on_delete=models.CASCADE)

    active = models.BooleanField()
    read_only = models.BooleanField()


class Scope(models.Model):
    name = models.CharField(max_length=128)
    provider_id = models.ForeignKey(DataProvider,
                                    on_delete=models.CASCADE)
    description = models.TextField()


class PermissionGroup(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField()
    app_id = models.ForeignKey(App,
                        on_delete=models.CASCADE)
    scopes = models.ManyToManyField(Scope)


class PredefinedPolicy(models.Model):
    provider_id = models.ForeignKey(DataProvider,
                                    null=True,
                                    on_delete=models.SET_NULL)
    app_id = models.ForeignKey(App,
                               on_delete=models.CASCADE)
    approved = models.BooleanField()
    group_id = models.ForeignKey(PermissionGroup,
                                 on_delete=models.CASCADE)

class Function(models.Model):
    name = models.CharField(max_length=128)
    body = models.TextField()
    app_id = models.ForeignKey(App,
                               on_delete=models.CASCADE)
    description = models.TextField()
    approved = models.BooleanField()

class Token(models.Model):
    user_id = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    provider_id = models.ForeignKey(DataProvider,
                                    on_delete=models.CASCADE)
    token_type = models.TextField()
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_on = models.DateTimeField()


class PrivateData(models.Model):
    user_id = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    provider_id = models.ForeignKey(DataProvider,
                                    on_delete=models.CASCADE)
    value = fields.JSONField()
