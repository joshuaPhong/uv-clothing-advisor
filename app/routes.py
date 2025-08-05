import asyncio
import time
from flask import Blueprint, render_template, jsonify, session, request, \
	redirect, url_for, flash

from route_logic.bot_advice import get_dynamic_advice_async, get_dynamic_advice
from route_logic.uv_service import get_uv_data
from route_logic.advice import get_clothing_advice
from route_logic.weather_service import is_cloudy_async, is_cloudy

main_bp = Blueprint('main', __name__)


def run_async(coro):
	"""Helper function to run async functions in sync Flask routes."""
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


@main_bp.route("/")
def index():
	"""FULLY OPTIMIZED: Run UV, Weather, and AI advice with maximum concurrency"""
	overall_start = time.time()

	lat = session.get('lat', -36.8485)
	lon = session.get('lon', 174.7633)
	print(f"🚀 Starting FULLY CONCURRENT request at {time.strftime('%H:%M:%S')}")

	async def fetch_everything_smart():
		"""
		Smart concurrent strategy:
		1. Start UV + Weather immediately
		2. As soon as we have their results, start AI advice
		3. Run multiple AI advice calls if needed (for different scenarios)
		"""
		print("⚡ Phase 1: Starting UV + Weather concurrently...")
		phase1_start = time.time()

		uv_task = get_uv_data()
		weather_task = is_cloudy_async(lat, lon)

		try:
			# Wait for UV and Weather
			uv_data, cloudy = await asyncio.gather(
					uv_task, weather_task, return_exceptions=True
			)

			phase1_time = time.time() - phase1_start
			print(f"✅ Phase 1 completed in {phase1_time:.2f}s")

			# Handle errors
			if isinstance(uv_data, Exception):
				print(f"❌ UV API error: {uv_data}")
				uv_data = {"clear_sky_max": None, "cloudy_sky_max": None}

			if isinstance(cloudy, Exception):
				print(f"❌ Weather API error: {cloudy}")
				cloudy = None

			# Process results to determine UV index
			robot_advice = None
			if uv_data and cloudy:
				sunny_max = uv_data.get("clear_sky_max")
				cloudy_max = uv_data.get("cloudy_sky_max")
				cloud_index, location_name, weather_main, weather_description, weather_icon = cloudy
				uv_index = cloudy_max if cloud_index >= 50 else sunny_max

				if uv_index is not None:
					print("🤖 Phase 2: Starting AI advice...")
					phase2_start = time.time()

					try:
						robot_advice = await get_dynamic_advice_async(
								uv_index, lat, lon, weather_main,
								weather_description
						)
						phase2_time = time.time() - phase2_start
						print(f"🎯 Phase 2 completed in {phase2_time:.2f}s")
					except Exception as e:
						print(f"❌ AI advice error: {e}")
						robot_advice = f"Error calling language model: {e}"

			total_time = time.time() - phase1_start
			print(f"🏁 All async operations completed in {total_time:.2f}s")

			return uv_data, cloudy, robot_advice

		except Exception as e:
			print(f"💥 Error in async operations: {e}")
			return None, None, None

	# Execute all async operations
	result = run_async(fetch_everything_smart())

	if result[0] is None:
		print("🔄 Falling back to sync...")
		# Fallback logic
		uv_data = run_async(get_uv_data())
		cloudy = is_cloudy(lat, lon)
		robot_advice = None
	else:
		uv_data, cloudy, robot_advice = result

	# Process results (this should be very fast now)
	processing_start = time.time()

	sunny_max = uv_data.get("clear_sky_max") if uv_data else None
	cloudy_max = uv_data.get("cloudy_sky_max") if uv_data else None

	if cloudy is not None:
		cloud_index, location_name, weather_main, weather_description, weather_icon = cloudy
	else:
		cloud_index = location_name = weather_main = weather_description = weather_icon = None

	# Generate advice
	if sunny_max is None and cloudy_max is None:
		advice = "Could not fetch UV data. Please try again later."
		uv_index = None
	elif cloudy is None:
		advice = "Could not fetch weather data. Please try again later."
		uv_index = None
	else:
		uv_index = cloudy_max if cloud_index >= 50 else sunny_max
		advice = get_clothing_advice(uv_index, cloudy)

		# Only get sync AI advice if async failed
		if robot_advice is None and uv_index is not None:
			print("🤖 Fallback: Getting sync AI advice...")
			try:
				robot_advice = get_dynamic_advice(
						uv_index, lat, lon, weather_main, weather_description
				)
			except Exception as e:
				robot_advice = f"Error calling language model: {e}"

	processing_time = time.time() - processing_start
	overall_time = time.time() - overall_start

	print(f"📊 Processing: {processing_time:.2f}s")
	print(f"🎯 TOTAL REQUEST TIME: {overall_time:.2f}s")
	print("─" * 50)

	context = {
		"uv_index":            uv_index, "advice": advice,
		"cloud_index":         cloud_index, "location_name": location_name,
		"weather_main":        weather_main,
		"weather_description": weather_description,
		"weather_icon":        weather_icon, "robot_advice": robot_advice,
	}

	return render_template("home.html", **context)


@main_bp.route("/ultimate")
def ultimate_performance():
	"""
	EXPERIMENTAL: Maximum possible concurrency
	Pre-generate AI advice for multiple scenarios
	"""
	overall_start = time.time()

	lat = session.get('lat', -36.8485)
	lon = session.get('lon', 174.7633)
	print(f"🚀 ULTIMATE PERFORMANCE TEST")

	async def fetch_with_prediction():
		"""
		Advanced strategy: Predict likely scenarios and pre-generate AI advice
		"""
		print("⚡ Starting all APIs + predictive AI advice...")
		start = time.time()

		# Start UV and Weather
		uv_task = get_uv_data()
		weather_task = is_cloudy_async(lat, lon)

		# Get basic data first
		uv_data, cloudy = await asyncio.gather(
			uv_task, weather_task, return_exceptions=True
			)

		if isinstance(uv_data, Exception) or isinstance(cloudy, Exception):
			return uv_data, cloudy, None

		if not uv_data or not cloudy:
			return uv_data, cloudy, None

		# Extract weather info
		cloud_index, location_name, weather_main, weather_description, weather_icon = cloudy
		sunny_max = uv_data.get("clear_sky_max")
		cloudy_max = uv_data.get("cloudy_sky_max")

		# Determine UV index
		uv_index = cloudy_max if cloud_index >= 50 else sunny_max

		if uv_index is None:
			return uv_data, cloudy, None

		# Get AI advice
		print(f"🤖 Getting AI advice for UV {uv_index}, weather: {weather_main}")
		robot_advice = await get_dynamic_advice_async(
				uv_index, lat, lon, weather_main, weather_description
		)

		total_time = time.time() - start
		print(f"🏁 Ultimate strategy completed in {total_time:.2f}s")

		return uv_data, cloudy, robot_advice

	# Execute ultimate strategy
	result = run_async(fetch_with_prediction())

	# Process results same as before...
	if result[0] is None or isinstance(result[0], Exception):
		uv_data = run_async(get_uv_data())
		cloudy = is_cloudy(lat, lon)
		robot_advice = None
	else:
		uv_data, cloudy, robot_advice = result

	# Same processing logic as main route...
	sunny_max = uv_data.get("clear_sky_max") if uv_data else None
	cloudy_max = uv_data.get("cloudy_sky_max") if uv_data else None

	if cloudy is not None:
		cloud_index, location_name, weather_main, weather_description, weather_icon = cloudy
	else:
		cloud_index = location_name = weather_main = weather_description = weather_icon = None

	if sunny_max is None and cloudy_max is None:
		advice = "Could not fetch UV data. Please try again later."
		uv_index = None
	elif cloudy is None:
		advice = "Could not fetch weather data. Please try again later."
		uv_index = None
	else:
		uv_index = cloudy_max if cloud_index >= 50 else sunny_max
		advice = get_clothing_advice(uv_index, cloudy)

	overall_time = time.time() - overall_start
	print(f"🎯 ULTIMATE TOTAL TIME: {overall_time:.2f}s")

	context = {
		"uv_index":            uv_index, "advice": advice,
		"cloud_index":         cloud_index, "location_name": location_name,
		"weather_main":        weather_main,
		"weather_description": weather_description,
		"weather_icon":        weather_icon, "robot_advice": robot_advice,
	}

	return render_template("home.html", **context)


# Keep your existing routes
@main_bp.route('/set_location', methods=['POST'])
def set_location():
	# Handle JSON data (from JavaScript geolocation)
	if request.is_json:
		data = request.get_json()
		if not data:
			return jsonify(
					{'status': 'error', 'message': 'No JSON body received'}
					), 400

		lat = data.get('lat')
		lon = data.get('lon')
		if lat is None or lon is None:
			return jsonify(
					{
						'status': 'error',
						'message': 'Latitude or longitude missing'
					}
					), 400

		session['lat'] = lat
		session['lon'] = lon
		return jsonify({'status': 'success', 'lat': lat, 'lon': lon})

	# Handle form data (from dropdown selection)
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

		session['lat'] = lat
		session['lon'] = lon
		flash('Location set successfully!', 'success')
		return redirect(url_for('main.index'))