from flask import *
import os
from project import app, db, bcrypt
from datetime import datetime
from project.model import Post, User, Comment
from project.form import RegistrationForm, LoginForm, CommentForm
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import desc, asc
from werkzeug.utils import secure_filename

# Home Page
@app.route('/', methods=['GET', 'POST'])
def posts():
    select = request.form.get('comp_select')
    form = LoginForm()
    if str(select) == "1":
        posts = Post.query.order_by(asc(Post.date_posted)).all()
    else:
        posts = Post.query.order_by(desc(Post.date_posted)).all()
    return render_template("posts.html", posts=posts, form=form)

# Introduce Page
@app.route('/info')
def index():
    form = LoginForm()
    return render_template("index.html", form=form)

# Admin Panel pages
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def all_posts():
    if current_user.permissions == 'admin':
        form = RegistrationForm()
        posts = Post.query.order_by(desc(Post.date_posted)).all()
        return render_template("admin_panel/all_posts.html", posts=posts, form=form)
    else:
        return redirect('/')

# Post Modifying
@app.route('/admin/modify', methods=['GET', 'POST'])
@login_required
def modify():
    if current_user.permissions == 'admin':
        form = LoginForm()
        posts = Post.query.order_by(desc(Post.date_posted)).all()
        return render_template("admin_panel/modify_posts.html", posts=posts, form=form)
    else:
        return redirect('/')

# Showing all users (Admin Panel)
@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def all_users():
    if current_user.permissions == 'admin':
        users = User.query.all()
        return render_template("admin_panel/all_users.html", users=users)
    else:
        return redirect('/')

# Adding user (Admin Panel)
@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.permissions == 'admin':
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
    else:
        return redirect('/')

# Delating user (Admin Panel)
@app.route('/users/delete_user/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    if current_user.permissions == 'admin':
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return redirect('/admin/users')
    else:
        return redirect('/')

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



# Showing content in post (read more)
@app.route('/post/more/<int:id>', methods=['GET', 'POST'])
def more(id):
    select = request.form.get('comment_select')
    if str(select) == '1':
        comments = Comment.query.order_by(asc(Comment.time)).all()
    else:
        comments = Comment.query.order_by(desc(Comment.time)).all()

    form = RegistrationForm()
    posts = Post.query.get_or_404(id)
    comments_count = Comment.query.filter_by(post_id=id).count()
    users = User.query.all()
    Commentform = CommentForm()

    if Commentform.validate_on_submit():
        author_id = current_user.id
        comment = Comment(author=author_id,
                          body=Commentform.Comment.data, post_id=id)
        db.session.add(comment)
        db.session.commit()
        return redirect(request.url)
    return render_template("post.html", posts=posts, form=form, comment=Commentform,
                           comments=comments, users=users, comments_count=comments_count)

# Adding new post (Admin Panel)
@app.route('/admin/new', methods=['GET', 'POST'])
@login_required
def new():
    if current_user.permissions == 'admin':
        if request.method == "POST":
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))

            post_image_file = filename
            post_title = request.form['title']
            post_content = request.form['content']
            post_author = request.form['author']
            new_post = Post(image_file=post_image_file, title=post_title,
                            content=post_content, author=post_author)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/')
        else:
            return render_template("admin_panel/new_post.html")
    else:
        return redirect('/')
        
# Deleting comments(delete button in comment)
@app.route('/post/more/deletecom/<int:id>', methods=['GET', 'POST'])
@login_required
def deletecom(id):
    if current_user.permissions == 'admin':
        comment = Comment.query.get_or_404(id)
        db.session.delete(comment)
        db.session.commit()
        return redirect('/')

# Deleting posts (Panel Admin in modify post section)
@app.route('/post/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    if current_user.permissions == 'admin':
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()
        return redirect('/admin/modify')
    else:
        return redirect('/')

# Allowed files to upload (allowed extensions)
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Editing post
@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user.permissions == 'admin':
        if request.method == "POST":
            file = request.files['edit_file']
            if file.filename == '':
                img = post.image_file
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
                img = filename

            post.image_file = img
            post.title = request.form['edit_title']
            post.content = request.form['edit_content']
            post.author = request.form['edit_author']
            db.session.commit()
            return redirect('/')
        else:
            return render_template("admin_panel/edit_posts.html", post=post)
    else:
        return redirect('/')