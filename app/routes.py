# app/routes.py

from flask import Blueprint, render_template, jsonify, session, request
from route_logic.uv_service import get_uv_data
from route_logic.advice import get_clothing_advice
from route_logic.weather_service import is_cloudy

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
	lat = session.get('lat', -36.8485)
	lon = session.get('lon', 174.7633)
	print(f"Using coordinates: lat={lat}, lon={lon}")

	uv_max = get_uv_data()
	cloudy = is_cloudy(lat, lon)

	if uv_max is None:
		advice = "Could not fetch UV data. Please try again later."
	elif cloudy is None:
		advice = "Could not fetch weather data. Please try again later."
	else:
		advice = get_clothing_advice(uv_max, cloudy)

	cloud_index, location_name, weather_main, weather_description, weather_icon = cloudy if cloudy is not None else (None, None)

	context = {
		"uv_index": uv_max,
		"advice": advice,
		"cloud_index": cloud_index,
		"location_name": location_name,
		"weather_main": weather_main,
		"weather_description": weather_description,
		"weather_icon": weather_icon,
	}

	return render_template("test_css.html", **context)


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
