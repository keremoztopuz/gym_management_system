from wtforms import Form, StringField, PasswordField, validators, IntegerField

class LoginForm(Form):
    email = StringField("Email", validators=[validators.Length(min=7, max=50), validators.DataRequired(message="Please Fill This Field")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please Fill This Field")])

class RegisterForm(Form):
    name = StringField("Name", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    username = StringField("Username", validators=[validators.Length(min=3, max=25), validators.DataRequired(message="Please Fill This Field")])
    email = StringField("Email", validators=[validators.Email(message="Please enter a valid email address")])
    password = PasswordField("Password", validators=[
        validators.DataRequired(message="Please Fill This Field"),
        validators.EqualTo(fieldname="confirm", message="Your Passwords Do Not Match")
    ])
    confirm = PasswordField("Confirm Password", validators=[validators.DataRequired(message="Please Fill This Field")])
    weight = IntegerField("Weight", validators=[validators.NumberRange(min=30, max=150), validators.DataRequired(message="Please Fill This Field")])
    height = IntegerField("Height", validators=[validators.NumberRange(min=140, max=230), validators.DataRequired(message="Please Fill This Field")])
    location = StringField("Location", validators=[validators.AnyOf(values=["Ankara","İzmir","İstanbul"]), validators.DataRequired(message="Please Fill This Field")])