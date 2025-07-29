import os
import requests
import logging

DEFAULT_LOCATION = {"lat": -36.8485, "lon": 174.7633}
OWM_API_URL = "https://api.openweathermap.org/data/2.5/weather"


def is_cloudy(lat, lon):
	open_weather_key = os.getenv("OPEN_WEATHER_KEY")
	params = {
		"lat":   lat, "lon": lon,
		"appid": open_weather_key, "units": "metric"
		# optional, in case you want temps later
	}

	try:
		r = requests.get(OWM_API_URL, params=params)
		r.raise_for_status()
		payload = r.json()

		# Use cloud percentage
		# cloud_pct = payload.get("clouds", {}).get("all", 0)
		cloud_index = payload.get("clouds", {}).get("all", 0)
		print(payload)
		# Return True if mostly cloudy or overcast
		return cloud_index  # cloud_pct >= 50,

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
	return None  # could also return False as a fallback
