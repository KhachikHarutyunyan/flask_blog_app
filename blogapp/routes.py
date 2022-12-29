import os, secrets
from flask import request, flash, url_for, render_template, redirect, abort
from flask_login import current_user, login_required, logout_user, login_user
from PIL import Image
from blogapp import app, db, bcrypt, mail
from blogapp.forms import RegisterForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from blogapp.models import User, Post
from flask_mail import Message

@app.route("/")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template("home.html", title="Home", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegisterForm()
    if form.validate_on_submit():
        hash_pass = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hash_pass)
        db.session.add(user)
        db.session.commit()
        flash("Account has been created.Now you success to Login", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("home"))
        else:
            flash("Please check yor email and password", "danger")
            return redirect(url_for("login"))
    
    return render_template("login.html", title="Login", form=form)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("home"))

def save_picture(form_picture):
    random_name = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_name + f_ext
    picture_path = os.path.join(app.root_path, "static/images/profile_img", picture_name)
    print("PATH", picture_path)
    output = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output)
    i.save(picture_path)

    if current_user.image_file != "default.jpg":
        os.remove(os.path.join(app.root_path, "static/images/profile_img", current_user.image_file))

    return picture_name


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    
    if form.validate_on_submit():
        if form.picture.data:
            print("PICTURE", form.picture.data)
            picture = save_picture(form.picture.data)
            current_user.image_file = picture
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Account has been updated", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='images/profile_img/' + current_user.image_file)
    return render_template("account.html", title="Account", form=form, image_file=image_file)

@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Post has been created", "success")
        return redirect(url_for("home"))
    return render_template("new_post.html", title="Create post", form=form, legend="Create Post")

@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Post has been updated", "success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
        
    return render_template("new_post.html", title="Update post", form=form, legend="Update Post")

@app.route("/post/<int:post_id>/delete", methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post has been deleted", "success")

    return redirect(url_for("home"))

@app.route("/user/<string:username>")
def user_posts(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get("page", 1, type=int)
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template("user_posts.html", title="User posts", posts=posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request", sender="noreply@demo.com", recipients=[user.email])
    msg.body = f"""
        To reset your password, visit the following Link:
        {url_for(reset_token, token=token, _external=True)}
        If you do not make this request then simply ignore this email and no changes will be made.
    """

@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        print(user)
        send_reset_email(user)
        flash("An email has been send with instructions to reset your password", "info")
        return redirect(url_for("login"))

    return render_template("reset_request.html", title="Reset Password", form=form)

@app.route("/reset_password/<string:token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
        
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hash_pass = bcrypt.generate_password_hash(form.password.data)
        user.password = hash_pass
        db.session.commit()
        flash("Your password has been updated.Now you able to Login", "success")
        return redirect(url_for("login"))


    return render_template("reset_token.html", title="Reset Password", form=form)
