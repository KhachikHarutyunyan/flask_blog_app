import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SECRET_KEY"] = "84d2f2dd07c0132c3ed17b8830100562"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "site.db")

db = SQLAlchemy(app)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

login_manager.login_message_category = "info"
login_manager.login_view = "login"

# Email Configs
app.config["MAIL_SERVER"] = "smtp.mailtrap.io"
app.config["MAIL_PORT"] = 2525
app.config["MAIL_USERNAME"] = "35c3f3d60fef6c"
app.config["MAIL_PASSWORD"] = "143416bc3361c3"
# if use environment
# app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
# app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
mail = Mail(app)

from blogapp import routes