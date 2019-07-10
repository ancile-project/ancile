from flask_security.forms import RegisterForm, ConfirmRegisterForm
from wtforms.fields import SelectField

class CustomSelectField(SelectField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = [self.coerce(valuelist[0])]
            except ValueError:
                raise ValueError(self.gettext('Invalid Choice: could not coerce'))

    def pre_validate(self, form):
        for v, _ in self.choices:
            if self.data[0] == v:
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))


# extend registration form to include role field
class ExtendedRegisterForm(RegisterForm):
    roles = CustomSelectField(u'Role', choices=[("user", "User"), ("app", "Application")], default=["user"])

class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
    roles = CustomSelectField(u'Role', choices=[("user", "User"), ("app", "Application")], default=["user"])
