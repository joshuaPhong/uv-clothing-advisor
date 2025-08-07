import asyncio
import time
from flask import Blueprint, render_template, jsonify, session, request, \
	redirect, url_for, flash

from route_logic.bot_advice import get_dynamic_advice_async, get_dynamic_advice
from route_logic.uv_service import get_uv_data
from route_logic.advice import get_clothing_advice
from route_logic.weather_service import is_cloudy_async

main_bp = Blueprint('main', __name__)

# Cache duration in seconds (5 minutes)
CACHE_DURATION = 300


def run_async(coro):
	"""
	Helper function to run async functions in sync Flask routes.

	Handles different event loop scenarios:
	- If no loop exists, creates one and runs the coroutine
	- If a loop is running, uses ThreadPoolExecutor to avoid conflicts
	- Falls back to asyncio.run() if other methods fail

	Args:
		coro: Coroutine to execute

	Returns:
		Result of the coroutine execution
	"""
	try:
		loop = asyncio.get_event_loop()
		if loop.is_running():
			import concurrent.futures
			with concurrent.futures.ThreadPoolExecutor() as executor:
				future = executor.submit(asyncio.run, coro)
				return future.result()
		else:
			return loop.run_until_complete(coro)
	except RuntimeError:
		return asyncio.run(coro)


def get_location_key(lat, lon):
	"""Generate a cache key for the given coordinates."""
	return f"{round(lat, 4)}_{round(lon, 4)}"


def is_cache_valid(cache_timestamp):
	"""Check if cached data is still valid based on timestamp."""
	return cache_timestamp and (time.time() - cache_timestamp) < CACHE_DURATION


def should_fetch_new_data(lat, lon):
	"""
	Determine if new API calls are needed based on location change and cache age.

	Returns:
		tuple: (should_fetch, reason) where reason explains why fetching is needed
	"""
	location_key = get_location_key(lat, lon)
	cached_location_key = session.get('cached_location_key')
	cache_timestamp = session.get('cache_timestamp')

	# Location has changed
	if cached_location_key != location_key:
		return True, "location_changed"

	# Cache has expired
	if not is_cache_valid(cache_timestamp):
		return True, "cache_expired"

	# Cache is still valid
	return False, "cache_valid"


@main_bp.route("/")
def index():
	"""
	Main route that provides UV index and weather-based clothing advice.

	Now includes intelligent caching:
	- Only makes API calls when location changes or cache expires
	- Stores cached data in session with timestamps
	- Falls back to fresh API calls if cache is corrupted

	Session variables:
		lat (float): Latitude coordinate (defaults to Auckland: -36.8485)
		lon (float): Longitude coordinate (defaults to Auckland: 174.7633)
		cached_location_key (str): Key representing cached location
		cache_timestamp (float): When the data was last cached
		cached_context (dict): Cached template context data

	Returns:
		Rendered home.html template with context containing:
		- uv_index: Current UV index based on weather conditions
		- advice: Clothing advice based on UV levels
		- cloud_index: Cloud coverage percentage
		- location_name: Name of the location
		- weather_main: Main weather condition
		- weather_description: Detailed weather description
		- weather_icon: Weather icon code
		- robot_advice: AI-generated personalized advice
		- is_nighttime: Boolean indicating if it's nighttime
	"""
	lat = session.get('lat', -36.8485)
	lon = session.get('lon', 174.7633)

	# Check if we need to fetch new data
	should_fetch, reason = should_fetch_new_data(lat, lon)

	# Try to use cached data if available and valid
	if not should_fetch:
		cached_context = session.get('cached_context')
		if cached_context and isinstance(cached_context, dict):
			# Add a flag to indicate this is cached data (optional, for debugging)
			cached_context['from_cache'] = True
			return render_template("home.html", **cached_context)

	# If we reach here, we need fresh data
	print(f"Fetching fresh data - reason: {reason}")

	async def fetch_everything_smart():
		"""
		Concurrent data fetching strategy:
		1. Start UV and Weather API calls simultaneously
		2. Check if it's nighttime from weather data
		3. Only generate AI advice during daytime

		Returns:
			tuple: (uv_data, cloudy, robot_advice, is_nighttime) or (None, None, None, False) on error
		"""
		# Start UV and weather requests concurrently
		uv_task = get_uv_data()
		weather_task = is_cloudy_async(lat, lon)

		try:
			# Wait for both API calls to complete
			uv_data, cloudy = await asyncio.gather(
					uv_task, weather_task, return_exceptions=True
			)

			# Handle API errors
			if isinstance(uv_data, Exception):
				uv_data = {"clear_sky_max": None, "cloudy_sky_max": None}

			if isinstance(cloudy, Exception):
				cloudy = None

			# Check if it's nighttime first to avoid unnecessary AI calls
			is_nighttime = False
			robot_advice = None

			if cloudy and isinstance(cloudy, (tuple, list)) and len(
					cloudy
			) >= 7:
				# Unpack weather data: (cloud_index, location_name, weather_main, weather_description, weather_icon, sunrise, sunset)
				cloud_index, location_name, weather_main, weather_description, weather_icon, sunrise, sunset = cloudy

				# Check if it's nighttime using sunrise/sunset data
				if sunrise and sunset:
					now = time.time()
					is_nighttime = not (sunrise <= now <= sunset)

				# Only generate AI advice during daytime
				if not is_nighttime and uv_data:
					sunny_max = uv_data.get("clear_sky_max")
					cloudy_max = uv_data.get("cloudy_sky_max")

					uv_index = cloudy_max if cloud_index >= 50 else sunny_max

					if uv_index is not None:
						try:
							robot_advice = await get_dynamic_advice_async(
									uv_index, lat, lon, weather_main,
									weather_description
							)
						except Exception as e:
							robot_advice = f"Error calling language model: {e}"

			return uv_data, cloudy, robot_advice, is_nighttime

		except Exception:
			return None, None, None, False

	# Execute async operations
	result = run_async(fetch_everything_smart())

	# Fallback to sync operations if async failed
	if result[0] is None:
		uv_data = run_async(get_uv_data())
		cloudy = run_async(is_cloudy_async(lat, lon))
		robot_advice = None
		is_nighttime = False
	else:
		uv_data, cloudy, robot_advice, is_nighttime = result

	# Initialize default context
	context = {
		"uv_index":            None, "advice": "No data available.",
		"cloud_index":         None, "location_name": None,
		"weather_main":        None, "weather_description": None,
		"weather_icon":        None, "robot_advice": None,
		"is_nighttime":        is_nighttime, "from_cache": False
	}

	# Process weather and UV data (works for both day and night)
	if cloudy and isinstance(cloudy, (tuple, list)) and len(cloudy) >= 7:
		# Unpack weather data: (cloud_index, location_name, weather_main, weather_description, weather_icon, sunrise, sunset)
		cloud_index, location_name, weather_main, weather_description, weather_icon, sunrise, sunset = cloudy

		if is_nighttime:
			# Nighttime: Show weather data but no UV advice or AI advice
			context.update(
					{
						"location_name":       location_name,
						"weather_main":        weather_main,
						"weather_description": weather_description,
						"weather_icon":        weather_icon,
						"advice":              "It's nighttime! No UV protection needed.",
						"robot_advice":        "Enjoy your evening! UV levels are not a concern during nighttime hours."
					}
			)
		else:
			# Daytime: Process UV data and show full advice
			sunny_max = uv_data.get("clear_sky_max") if uv_data else None
			cloudy_max = uv_data.get("cloudy_sky_max") if uv_data else None

			if sunny_max is None and cloudy_max is None:
				advice = "Could not fetch UV data. Please try again later."
				uv_index = None
			else:
				uv_index = cloudy_max if cloud_index >= 50 else sunny_max
				# Pass the first 5 elements to get_clothing_advice (it expects 5)
				advice = get_clothing_advice(uv_index, cloudy[:5])

				# Get sync AI advice if async failed and we don't have it yet
				if robot_advice is None and uv_index is not None:
					try:
						robot_advice = get_dynamic_advice(
								uv_index, lat, lon, weather_main,
								weather_description
						)
					except Exception as e:
						robot_advice = f"Error calling language model: {e}"

			context.update(
					{
						"uv_index":            uv_index, "advice": advice,
						"cloud_index":         cloud_index,
						"location_name":       location_name,
						"weather_main":        weather_main,
						"weather_description": weather_description,
						"weather_icon":        weather_icon,
						"robot_advice":        robot_advice,
					}
			)
	else:
		# No valid weather data available
		context[
			"advice"] = "Could not fetch weather data. Please try again later."

	# Cache the context data for future requests
	location_key = get_location_key(lat, lon)
	session['cached_location_key'] = location_key
	session['cache_timestamp'] = time.time()
	session[
		'cached_context'] = context.copy()  # Store a copy to avoid reference issues

	return render_template("home.html", **context)


@main_bp.route('/set_location', methods=['POST'])
def set_location():
	"""
	Handle location setting from both JSON (geolocation API) and form data.

	Accepts two types of requests:
	1. JSON data from JavaScript geolocation API with 'lat' and 'lon' fields
	2. Form data with 'lat_lon' field containing comma-separated coordinates

	Stores location coordinates in the user's session and clears cache if location changed.

	Returns:
		For JSON requests: JSON response with status and coordinates
		For form requests: Redirect to index with flash message

	Error responses:
		400: Missing or invalid data
		Redirect with error flash for form submissions
	"""
	old_lat = session.get('lat')
	old_lon = session.get('lon')

	# Handle JSON data from JavaScript geolocation API
	if request.is_json:
		data = request.get_json()
		if not data:
			return jsonify(
					{
						'status': 'error', 'message': 'No JSON body received'
					}
			), 400

		lat = data.get('lat')
		lon = data.get('lon')
		if lat is None or lon is None:
			return jsonify(
					{
						'status':  'error',
						'message': 'Latitude or longitude missing'
					}
			), 400

		# Check if location actually changed before clearing cache
		if old_lat != lat or old_lon != lon:
			# Clear cache when location changes
			session.pop('cached_location_key', None)
			session.pop('cache_timestamp', None)
			session.pop('cached_context', None)

		session['lat'] = lat
		session['lon'] = lon
		return jsonify({'status': 'success', 'lat': lat, 'lon': lon})

	# Handle form data from dropdown selection
	else:
		lat_lon = request.form.get('lat_lon')
		if not lat_lon:
			flash('Please select a location', 'error')
			return redirect(url_for('main.index'))

		try:
			lat, lon = lat_lon.split(',')
			lat = float(lat)
			lon = float(lon)
		except (ValueError, AttributeError):
			flash('Invalid location format', 'error')
			return redirect(url_for('main.index'))

		# Check if location actually changed before clearing cache
		if old_lat != lat or old_lon != lon:
			# Clear cache when location changes
			session.pop('cached_location_key', None)
			session.pop('cache_timestamp', None)
			session.pop('cached_context', None)

		session['lat'] = lat
		session['lon'] = lon
		flash('Location set successfully!', 'success')
		return redirect(url_for('main.index'))


@main_bp.route('/clear_cache', methods=['POST'])
def clear_cache():
	"""
	Utility route to manually clear the cache.
	Useful for debugging or forcing fresh data.
	"""
	session.pop('cached_location_key', None)
	session.pop('cache_timestamp', None)
	session.pop('cached_context', None)
	flash('Cache cleared successfully!', 'info')
	return redirect(url_for('main.index'))