from flask import request, render_template, Blueprint
from blogapp.models import Post
main = Blueprint("main", __name__)


@main.route("/")
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template("home.html", title="Home", posts=posts)

@main.route("/about")
def about():
    return render_template("about.html", title="About")

