import os
import aiohttp
import asyncio
import logging

OWM_API_URL = "https://api.openweathermap.org/data/2.5/weather"


async def is_cloudy_async(lat=-36.8485, lon=174.7633, session=None):
	"""
	Asynchronously fetch weather data from OpenWeatherMap API.

	Args:
		lat (float): Latitude coordinate (defaults to Auckland: -36.8485)
		lon (float): Longitude coordinate (defaults to Auckland: 174.7633)
		session (aiohttp.ClientSession, optional): Existing aiohttp session.
												   If None, creates a new one.

	Returns:
		tuple: (cloud_index, location_name, weather_main, weather_description,
				weather_icon, sunrise, sunset) containing:
			- cloud_index (int): Cloud coverage percentage (0-100)
			- location_name (str): Name of the location
			- weather_main (str): Main weather condition (e.g., "Clear", "Rain")
			- weather_description (str): Detailed weather description
			- weather_icon (str): Weather icon code from OpenWeatherMap
			- sunrise (int): Sunrise time as Unix timestamp
			- sunset (int): Sunset time as Unix timestamp
		None: If API call fails or encounters an error
	"""
	open_weather_key = os.getenv("OPEN_WEATHER_KEY")

	if not open_weather_key:
		logging.error(
			"OpenWeatherMap API key not found in environment variables"
			)
		return None

	params = {
		"lat": lat, "lon": lon, "appid": open_weather_key, "units": "metric"
	}

	# Use provided session or create a new one
	close_session = session is None
	if session is None:
		session = aiohttp.ClientSession()

	try:
		async with session.get(OWM_API_URL, params=params) as response:
			response.raise_for_status()
			payload = await response.json()

			# Extract cloud coverage percentage
			cloud_index = payload.get("clouds", {}).get("all", 0)
			location_name = payload.get("name", "Unknown Location")

			# Extract weather information
			weather_data = payload.get("weather", [{}])[0]
			weather_main = weather_data.get("main", "Unknown")
			weather_description = weather_data.get(
				"description", "No description"
				)
			weather_icon = weather_data.get("icon", "Unknown")

			# Extract sunrise/sunset data for day/night detection
			sys_data = payload.get("sys", {})
			sunrise = sys_data.get("sunrise", 0)
			sunset = sys_data.get("sunset", 0)

			return (
			cloud_index, location_name, weather_main, weather_description,
			weather_icon, sunrise, sunset)

	except aiohttp.ClientResponseError as http_err:
		logging.error(
				f"HTTP error occurred: {http_err}. Status: {http_err.status}, "
				f"Message: {http_err.message}"
		)
	except aiohttp.ClientConnectionError as conn_err:
		logging.error(f"Connection error occurred: {conn_err}")
	except asyncio.TimeoutError as timeout_err:
		logging.error(f"Timeout error occurred: {timeout_err}")
	except Exception as err:
		logging.error(f"Unexpected error occurred: {err}")

	finally:
		# Only close session if we created it
		if close_session:
			await session.close()

	return None