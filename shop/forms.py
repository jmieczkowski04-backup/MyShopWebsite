from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, ValidationError, IntegerField, SearchField
from wtforms.validators import Length, Email, EqualTo, DataRequired
from shop.models import User, Item


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError("This username is used")

    def validate_email(self, email_to_check):
        user = User.query.filter_by(email=email_to_check.data).first()
        if user:
            raise ValidationError("This email is used")

    username = StringField(label="Username", validators=[Length(min=2, max=12), DataRequired()])
    email = EmailField(label="Email", validators=[Email(), DataRequired()],)
    password1 = PasswordField(label="Password", validators=[Length(min=2, max=12), DataRequired()])
    password2 = PasswordField(label="Confirm Password", validators=[EqualTo("password1"), DataRequired()])
    accept = BooleanField(label="Agree to terms and conditions", validators=[DataRequired()])
    submit = SubmitField(label="Create Account")


class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    remember_me = BooleanField(label="Remember me")
    submit = SubmitField(label="Login")

    def __init__(self,*k,**kk):
      self._user = None
      super(LoginForm,self).__init__(*k,**kk)

    def validate(self, *k, **kk):
       self._user = User.query.filter_by(username=self.username.data).first()
       return super(LoginForm, self).validate(*k, **kk)

    def validate_username(self, field):
       if self._user is None:
           raise ValidationError("This user doesn't exist")

    def validate_password(self, field):
       if self._user is None:
           raise ValidationError()
       if not self._user.check_password(self.password.data):
           raise ValidationError("Password incorrect")


class AddToCartForm(FlaskForm):
    amount = IntegerField(label="Amount", validators=[DataRequired()])
    submit = SubmitField(label="submit")


class ChangeAmountForm(FlaskForm):
    minus_submit = SubmitField(label="-")
    plus_submit = SubmitField(label="+")
    delete_submit = SubmitField(label="Delete")


class BuyForm(FlaskForm):
    pass


class SearchForm(FlaskForm):
    search_input = SearchField(label="name", validators=[DataRequired()])
    submit = SubmitField(label="Search")
