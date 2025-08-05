import os
import aiohttp
import asyncio
import logging

DEFAULT_LOCATION = {"lat": -36.8485, "lon": 174.7633}
OWM_API_URL = "https://api.openweathermap.org/data/2.5/weather"


async def is_cloudy_async(lat=-36.8485, lon=174.7633, session=None):
	"""
	Asynchronously fetch weather data from OpenWeatherMap API.

	Args:
		lat: Latitude
		lon: Longitude
		session: Optional aiohttp session. If None, creates a new one.

	Returns:
		Tuple: (cloud_index, location_name, weather_main, weather_description, weather_icon)
		or None if error occurs
	"""
	open_weather_key = os.getenv("OPEN_WEATHER_KEY")

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

			# Use cloud percentage
			cloud_index = payload.get("clouds", {}).get("all", 0)
			location_name = payload.get("name", "Unknown Location")

			# Gather more data for the bot prompt
			weather_data = payload.get("weather", [{}])[0]
			weather_main = weather_data.get("main", "Unknown")
			weather_description = weather_data.get(
				"description", "No description"
				)
			weather_icon = weather_data.get("icon", "Unknown")

			return cloud_index, location_name, weather_main, weather_description, weather_icon

	except aiohttp.ClientResponseError as http_err:
		logging.error(
				f"HTTP error occurred: {http_err}. Status: {http_err.status}, Message: {http_err.message}"
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

	return None  # could also return False as a fallback


# Keep the original sync version for backward compatibility
def is_cloudy(lat=-36.8485, lon=174.7633):
	"""
	Original synchronous version - kept for backward compatibility
	"""
	import requests

	open_weather_key = os.getenv("OPEN_WEATHER_KEY")
	params = {
		"lat": lat, "lon": lon, "appid": open_weather_key, "units": "metric"
	}

	try:
		r = requests.get(OWM_API_URL, params=params)
		r.raise_for_status()
		payload = r.json()

		cloud_index = payload.get("clouds", {}).get("all", 0)
		location_name = payload.get("name", "Unknown Location")
		weather_data = payload.get("weather", [{}])[0]
		weather_main = weather_data.get("main", "Unknown")
		weather_description = weather_data.get("description", "No description")
		weather_icon = weather_data.get("icon", "Unknown")

		return cloud_index, location_name, weather_main, weather_description, weather_icon

	except requests.exceptions.HTTPError as http_err:
		logging.error(
				f"HTTP error occurred: {http_err}. Response: {http_err.response.content if http_err.response else 'No response'}"
		)
	except requests.exceptions.ConnectionError as conn_err:
		logging.error(f"Connection error occurred: {conn_err}")
	except requests.exceptions.Timeout as timeout_err:
		logging.error(f"Timeout error occurred: {timeout_err}")
	except Exception as err:
		logging.error(f"Unexpected error occurred: {err}")
	return None


# Example usage functions
async def main_single():
	"""Example: Single async weather request"""
	print("Fetching weather data asynchronously...")
	weather_data = await is_cloudy_async()
	if weather_data:
		cloud_index, location_name, weather_main, weather_description, weather_icon = weather_data
		print(f"Location: {location_name}")
		print(f"Cloud coverage: {cloud_index}%")
		print(f"Weather: {weather_main} - {weather_description}")
	else:
		print("Failed to fetch weather data")


async def main_multiple_locations():
	"""Example: Multiple locations with shared session"""
	locations = [{"lat": -36.8485, "lon": 174.7633},  # Auckland
		{"lat": -41.2865, "lon": 174.7762},  # Wellington
		{"lat": -43.5321, "lon": 172.6362},  # Christchurch
	]

	async with aiohttp.ClientSession() as session:
		tasks = [is_cloudy_async(loc["lat"], loc["lon"], session) for loc in
			locations]
		results = await asyncio.gather(*tasks, return_exceptions=True)

		for i, result in enumerate(results):
			if isinstance(result, Exception):
				print(f"Error for location {i}: {result}")
			elif result:
				cloud_index, location_name, weather_main, weather_description, weather_icon = result
				print(f"{location_name}: {cloud_index}% clouds, {weather_main}")
			else:
				print(f"No data for location {i}")


if __name__ == "__main__":
	# Test the async version
	asyncio.run(main_single())

# Test multiple locations  # asyncio.run(main_multiple_locations())