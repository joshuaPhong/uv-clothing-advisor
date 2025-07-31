from flask import Blueprint
from . import auth_routes  # this registers the routes with the blueprint

auth_bp = Blueprint(
		"auth",
		__name__,
		template_folder='templates',
		url_prefix='/auth'
)
