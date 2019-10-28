def enforce_developer(func):
    def wrapped(self, info, **args):
        if info.context.user.is_developer:
            return func(self, info, **args)
    return wrapped

def enforce_admin(func):
    def wrapped(self, info, **args):
        if info.context.user.is_superuser:
            return func(self, info, **args)
    return wrapped

def enforce_either(func):
    def wrapped(self, info, **args):
        if info.context.user.is_superuser or info.context.user.is_developer:
            return func(self, info, **args)
    return wrapped