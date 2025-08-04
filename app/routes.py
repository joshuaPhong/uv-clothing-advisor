

from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for

from route_logic.bot_advice import get_dynamic_advice
from route_logic.uv_service import get_uv_data
from route_logic.advice import get_clothing_advice
from route_logic.weather_service import is_cloudy


main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
	lat = session.get('lat', -36.8485)
	lon = session.get('lon', 174.7633)
	print(f"Using coordinates: lat={lat}, lon={lon}")

	uv_data = get_uv_data()
	sunny_max = uv_data.get("clear_sky_max")
	cloudy_max = uv_data.get("cloudy_sky_max")
	cloudy = is_cloudy(lat, lon)

	if cloudy is not None:
		cloud_index, location_name, weather_main, weather_description, weather_icon = cloudy
	else:
		cloud_index, location_name, weather_main, weather_description, weather_icon = (
			None, None, None, None, None)

	robot_advice = None  # Ensure it's always defined

	if sunny_max is None and cloudy_max is None:
		advice = "Could not fetch UV data. Please try again later."
		uv_index = None
	elif cloudy is None:
		advice = "Could not fetch weather data. Please try again later."
		uv_index = None
	else:
		uv_index = cloudy_max if cloud_index >= 50 else sunny_max
		advice = get_clothing_advice(uv_index, cloudy)

		try:
			robot_advice = get_dynamic_advice(
					uv_index, lat, lon, weather_main, weather_description
			)
		except Exception as e:
			robot_advice = f"Error calling language model: {e}"

	context = {
		"uv_index":            uv_index, "advice": advice,
		"cloud_index":         cloud_index, "location_name": location_name,
		"weather_main":        weather_main,
		"weather_description": weather_description,
		"weather_icon":        weather_icon, "robot_advice": robot_advice,
	}

	return render_template("home.html", **context)


@main_bp.route('/set_location', methods=['POST'])
def set_location():
	data = request.get_json()

	if not data:
		return jsonify(
				{'status': 'error', 'message': 'No JSON body received'}
		), 400

	lat = data.get('lat')
	lon = data.get('lon')

	if lat is None or lon is None:
		return jsonify(
				{'status': 'error', 'message': 'Latitude or longitude missing'}
		), 400

	session['lat'] = lat
	session['lon'] = lon

	return jsonify({'status': 'success', 'lat': lat, 'lon': lon})


@main_bp.route('/user_location', methods=['POST'])
def user_location():
	lat = request.form.get('lat')
	lon = request.form.get('lon')

	if lat is None or lon is None:
		# Optionally flash a message or handle error
		return redirect(url_for('main.index'))

	try:
		session['lat'] = float(lat)
		session['lon'] = float(lon)
	except ValueError:
		# Handle invalid float conversion if needed
		return redirect(url_for('main.index'))

	return redirect(url_for('main.index'))
