from django.contrib import admin
from dashboard.models import *

# Register your models here.
admin.site.register(
    [
        User,
        App,
        DataProvider,
        Policy,
        Scope,
        PermissionGroup,
        PredefinedPolicy,
        Function,
        Token,
        PrivateData,
    ]
)
