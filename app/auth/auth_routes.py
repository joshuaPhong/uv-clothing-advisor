# app/auth/auth_routes.py
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from .auth_bp import auth_bp
from .forms import LoginForm, RegistrationForm
from .models import get_user_by_username, create_user


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
	print(
			f"Login route called, current_user.is_authenticated: {current_user.is_authenticated}"
	)
	print(f"Request method: {request.method}")

	# If user is already logged in, redirect to home
	if current_user.is_authenticated:
		print("User already authenticated, redirecting to home")
		return redirect(url_for('main.index'))

	form = LoginForm()
	print(f"Form validation result: {form.validate_on_submit()}")

	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		print(f"Login attempt - username: {username}")

		# Get user from database
		user = get_user_by_username(username)
		print(f"User found: {user is not None}")

		if user and user.check_password(password):
			print("Password correct, logging in user")
			# Log in with Flask-Login
			login_user(user, remember=form.remember_me.data)
			print("FLASHING SUCCESS MESSAGE")
			flash("Logged in successfully!", "success")

			# Handle next parameter for redirects after login
			next_page = request.args.get('next')
			if next_page:
				return redirect(next_page)
			else:
				return redirect(url_for('main.index'))
		else:
			print("FLASHING ERROR MESSAGE")
			print("Invalid username or password")
			flash("Invalid username or password.", "error")

	print("Rendering login template")
	return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
	print(
			f"Register route called, current_user.is_authenticated: {current_user.is_authenticated}"
	)

	if current_user.is_authenticated:
		print("User already logged in, redirecting to home")
		return redirect(url_for('main.index'))

	form = RegistrationForm()
	print(f"Form validation result: {form.validate_on_submit()}")

	if form.validate_on_submit():
		username = form.username.data
		email = form.email.data
		password = form.password.data
		print(f"Form data - username: {username}, email: {email}")

		user = create_user(username, email, password)
		print(f"create_user returned: {user}")

		if user:
			print("User created successfully, redirecting to login")
			flash("Registration successful! You can now log in.", "success")
			return redirect(url_for('auth.login'))
		else:
			print("User creation failed")
			flash(
					"Username already exists. Please choose a different one.",
					"error"
			)

	return render_template("auth/register.html", form=form)



@auth_bp.route("/logout")
@login_required
def logout():
	logout_user()
	flash("You have been logged out.", "info")
	return redirect(url_for("main.index"))


# Optional: Protected route example
@auth_bp.route("/profile")
@login_required
def profile():
	return render_template("auth/profile.html")
