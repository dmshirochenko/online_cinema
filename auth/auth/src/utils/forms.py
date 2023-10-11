from wtforms import BooleanField, EmailField, Form, PasswordField, StringField, validators


class SignUpForm(Form):
    username = StringField("Username", [validators.Length(min=4, max=25)])
    email = EmailField("Email", [validators.DataRequired(), validators.Email()])
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
            validators.Length(min=4, max=25),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Repeat password")
