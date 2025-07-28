import os
import requests

DEFAULT_LOCATION = {"lat": -36.8485, "long": 174.7633}
NIWA_KEY = os.getenv("NIWA_KEY")
NIWA_SECRET = os.getenv("NIWA_SECRET")
NIWA_API_URL = "https://api.niwa.co.nz/uv/data"


def get_uv_data():

	params = {
		"lat": DEFAULT_LOCATION["lat"], "long": DEFAULT_LOCATION["long"]
	}

	headers = {
		"x-apikey": NIWA_KEY, "Accept": "application/json"
	}

	try:
		r = requests.get(NIWA_API_URL, headers=headers, params=params)
		r.raise_for_status()
		payload = r.json()
		# Fix: Access 'products' instead of 'data'
		products = payload.get("products", [])

		# Find the clear_sky_uv_index product
		clear_sky_product = None
		for product in products:
			if product.get("name") == "clear_sky_uv_index":
				clear_sky_product = product
				break

		if clear_sky_product and "values" in clear_sky_product:
			# Extract UV values from the time series data
			uv_values = [entry["value"] for entry in clear_sky_product["values"]
			             if entry.get("value") is not None and entry.get(
						"value"
				) > 0]

			if uv_values:
				uv_max = max(uv_values)
			else:
				uv_max = None
		else:
			uv_max = None

	except Exception as e:
		uv_max = None
	return uv_max
