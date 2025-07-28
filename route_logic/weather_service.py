import os
import requests

DEFAULT_LOCATION = {"lat": -36.8485, "lon": 174.7633}
OWM_API_URL = "https://api.openweathermap.org/data/2.5/weather"


def is_cloudy():
	open_weather_key = os.getenv("OPEN_WEATHER_KEY")
	params = {
		"lat":   DEFAULT_LOCATION["lat"], "lon": DEFAULT_LOCATION["lon"],
		"appid": open_weather_key, "units": "metric"
		# optional, in case you want temps later
	}

	try:
		r = requests.get(OWM_API_URL, params=params)
		r.raise_for_status()
		payload = r.json()
		
		# Use cloud percentage
		cloud_pct = payload.get("clouds", {}).get("all", 0)

		# Return True if mostly cloudy or overcast
		return cloud_pct >= 50

	except Exception as e:
		print("Weather API error:", e)
		return None  # could also return False as a fallback
