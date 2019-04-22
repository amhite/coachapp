import os
import secrets
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from mifllteam import app, db, bcrypt
from mifllteam.models import User, Task, Post
from mifllteam.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, TaskForm
from flask_login import login_user, logout_user, current_user, login_required


# Main site
@app.route("/")
@app.route("/home")
def home():
	return render_template('home.html')

@app.route("/about")
def about():
	return render_template('about.html', title='About')


# User account
@app.route("/register", methods=["GET", "POST"])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, teamno=form.teamno.data, numberofmtgs=form.numberofmtgs.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in.', 'success')
		return redirect(url_for('login'))
	return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash("Log in unsuccessful. Pleaes check email and password.", "danger")
	return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updates!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('account.html', title='Account', image_file="default.jpg", form=form)

@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('update.html', title='Update', form=form)


#Tasks
@app.route("/tasks")
@login_required
def tasks():
	tasks = Task.query.all()
	rows = tasks.__len__()
	mtgs = current_user.numberofmtgs
	return render_template('tasks.html', title='Tasks', numMtgs=mtgs, tasks=tasks, numRows=rows)

@app.route("/task/new", methods = ['GET', 'POST'])
@login_required
def new_task():
	form = TaskForm()
	if form.validate_on_submit():
		task = Task(category = form.category.data, title = form.title.data, content = form.content.data)
		db.session.add(task)
		db.session.commit()
		flash('Your task has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_task.html', title='New Task', form=form, legend = "New Task")

#Engineering Notebook
@app.route("/notebook")
def notebook():
	posts=Post.query.all()
	return render_template('notebook.html', posts=posts)

@app.route("/post/new", methods = ['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title = form.title.data, content = form.content.data, author = current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('notebook'))
	return render_template('create_post.html', title='New Post', form=form, legend = "New Post")

@app.route("/post/<int:post_id>")
def post(post_id):
	post=Post.query.get_or_404(post_id)
	return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods = ['GET', 'POST'])
@login_required
def update_post(post_id):
	post=Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form=PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Your post has been updated!', 'success')
		return redirect(url_for('post', post_id=post.id))
	elif request.method == ('GET'):
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title='Update Post', form=form, legend="Update Post")

@app.route("/post/<int:post_id>/delete", methods = ['POST'])
@login_required
def delete_post(post_id):
	post=Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(url_for('notebook'))


# Tools
@app.route("/tools")
def tools():
	return render_template('tools.html', title='Tools')

@app.route("/timer")
def timer():
	return render_template('timer.html', title='Timer')

@app.route("/scorer")
def scorer():
	return render_template('scorer.html', title='Scorer')

@app.route("/links")
def links():
	return render_template('links.html', title='Links')