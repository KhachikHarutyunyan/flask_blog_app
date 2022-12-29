from flask import request, flash, url_for, render_template, redirect, Blueprint
from flask_login import current_user, login_required, logout_user, login_user
from blogapp import db, bcrypt
from .forms import RegisterForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from blogapp.models import User, Post
from .utils import save_picture, send_reset_email

users = Blueprint("users", __name__)

@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        hash_pass = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hash_pass)
        db.session.add(user)
        db.session.commit()
        flash("Account has been created.Now you success to Login", "success")
        return redirect(url_for("users.login"))
    return render_template("register.html", title="Register", form=form)

@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.home"))
        else:
            flash("Please check yor email and password", "danger")
            return redirect(url_for("users.login"))
    
    return render_template("login.html", title="Login", form=form)

@users.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    
    if form.validate_on_submit():
        if form.picture.data:
            picture = save_picture(form.picture.data)
            current_user.image_file = picture

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Account has been updated", "success")
        return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='images/profile_img/' + current_user.image_file)
    return render_template("account.html", title="Account", form=form, image_file=image_file)

@users.route("/user/<string:username>")
def user_posts(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get("page", 1, type=int)
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template("user_posts.html", title="User posts", posts=posts, user=user)

# RESET PASSWORD

@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been send with instructions to reset your password", "info")
        return redirect(url_for("users.login"))

    return render_template("reset_request.html", title="Reset Password", form=form)

@users.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
        
    user = User.verify_reset_token(token)

    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("users.reset_request"))
    
    form = ResetPasswordForm()
    if request.method == "POST":
        if form.validate_on_submit():
            hash_pass = bcrypt.generate_password_hash(form.password.data)
            user.password = hash_pass
            db.session.commit()
            flash("Your password has been updated.Now you able to Login", "success")
            return redirect(url_for("users.login"))
    
    return render_template("reset_token.html", title="Reset Password", form=form)
