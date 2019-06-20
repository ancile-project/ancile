from flask_security.forms import RegisterForm, ConfirmRegisterForm
from wtforms.fields import SelectMultipleField

# extend registration form to include role field
class ExtendedRegisterForm(RegisterForm):
    roles = SelectMultipleField(u'Role', choices=[("user", "User"), ("app", "Application")], default="user")

class ExtendedConfirmRegisterForm(ConfirmRegisterForm):
    roles = SelectMultipleField(u'Role', choices=[("user", "User"), ("app", "Application")], default="user")
