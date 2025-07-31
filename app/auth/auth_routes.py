from flask import render_template, redirect, url_for, request, flash, session
from .auth_bp import auth_bp


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		# 🔒 Dummy check (replace with real auth logic)
		if username == "admin" and password == "secret":
			session["user"] = username
			flash("Logged in successfully.")
			return redirect(url_for("main.index"))  # Change to your home route
		else:
			flash("Invalid credentials.")

	return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
	session.pop("user", None)
	flash("You were logged out.")
	return redirect(url_for("auth.login"))
