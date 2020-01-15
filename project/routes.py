from flask import *
import os
from project import app, db, bcrypt
from datetime import datetime
from project.model import Post, User
from project.form import RegistrationForm, LoginForm
from flask_login import current_user, login_user, logout_user
from sqlalchemy import desc, asc
from werkzeug.utils import secure_filename


@app.route('/', methods=['GET', 'POST'])
def posts():
    select = request.form.get('comp_select')
    form = LoginForm()
    if str(select) == "2":
        posts = Post.query.order_by(asc(Post.date_posted)).all()
    else:
        posts = Post.query.order_by(desc(Post.date_posted)).all()
    return render_template("posts.html", posts=posts, form=form)


@app.route('/info')
def index():
    form = LoginForm()
    return render_template("index.html", form=form)

# Admin Panel pages
@app.route('/admin', methods=['GET', 'POST'])
def all_posts():
    form = RegistrationForm()
    posts = Post.query.order_by(desc(Post.date_posted)).all()
    return render_template("admin_panel/all_posts.html", posts=posts, form=form)


@app.route('/admin/modify', methods=['GET', 'POST'])
def modify():
    form = LoginForm()
    posts = Post.query.order_by(desc(Post.date_posted)).all()
    return render_template("admin_panel/modify_posts.html", posts=posts, form=form)


@app.route('/admin/users', methods=['GET', 'POST'])
def all_users():
    users = User.query.all()
    return render_template("admin_panel/all_users.html", users=users)

# Adding user
@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password, permissions=form.permission.data)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    else:
        return render_template("admin_panel/new_user.html", form=form)


# Delating user
@app.route('/users/delete_user/<int:id>', methods=['GET', 'POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/admin/users')

# Login in
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    posts = Post.query.order_by(desc(Post.date_posted)).all()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            if user.permissions == "admin":
                return redirect('/admin')
            else:
                return redirect('/')
        else:
            return render_template('posts.html', form=form, posts=posts)

# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


# Registration
@app.route('/registration', methods=['GET', 'POST'])
def ragistration():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    else:
        return render_template("registration.html", form=form)

# Chacking file img


def allowed_image(filename):

    # Only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

# Posts interactions (editing, deleting, creating new)
@app.route('/admin/new', methods=['GET', 'POST'])
def new():
    if request.method == "POST":
        if request.files:
            image = request.files["file"]
            image.save(os.path.join(
                app.config["IMAGE_UPLOADS"], image.filename))
            print(image)

        post_image_file = image.filename
        post_title = request.form['title']
        post_content = request.form['content']
        post_author = request.form['author']
        new_post = Post(image_file=post_image_file, title=post_title,
                        content=post_content, author=post_author)
        db.session.add(new_post)
        db.session.commit()
        print("gitara")
        return redirect('/')
    else:
        return render_template("admin_panel/new_post.html")


@app.route('/posts/more/<int:id>', methods=['GET', 'POST'])
def more(id):
    form = RegistrationForm()
    posts = Post.query.get_or_404(id)
    return render_template("post.html", posts=posts, form=form)


@app.route('/posts/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    post = Post.query.get_or_404(id)
    if request.method == "POST":
        if request.files:
            image = request.files["edit_file"]
            image.save(os.path.join(
                app.config["IMAGE_UPLOADS"], image.filename))
            print(image)

        post._image_file = image.filename
        post.title = request.form['edit_title']
        post.content = request.form['edit_content']
        post.author = request.form['edit_author']
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template("admin_panel/edit_posts.html", post=post)
