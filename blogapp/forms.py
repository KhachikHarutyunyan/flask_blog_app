from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField, TextAreaField
from flask_wtf.file import FileAllowed, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from blogapp.models import User
from flask_login import current_user


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=30)])
    email = EmailField("Email", validators=[DataRequired(), Length(min=8, max=80), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username is taken.Please choose another one.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email is taken.Please choose another one.")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Length(min=8, max=80), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=30)])
    email = EmailField("Email", validators=[DataRequired(), Length(min=8, max=80), Email()])
    picture = FileField("Profile picture", validators=[FileAllowed(["png", "jpg"])])
    submit = SubmitField("Update")

    def validate_username(self, username):
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Username is taken.Please choose another one.")

    def validate_email(self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Email is taken.Please choose another one.")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=3, max=130)])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


class RequestResetForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Length(min=8, max=80), Email()])
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with that email. You must register first")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset Password")