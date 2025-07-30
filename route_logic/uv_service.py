import os
import requests

DEFAULT_LOCATION = {"lat": -36.8485, "long": 174.7633}
NIWA_API_URL = "https://api.niwa.co.nz/uv/data"


def extract_max_uv_value(product):
	"""Helper function to extract max UV value from a product."""
	if not product or "values" not in product:
		return None

	uv_values = [entry["value"] for entry in product["values"] if
	             entry.get("value") is not None and entry.get("value") > 0]

	return max(uv_values) if uv_values else None


def get_uv_data():
	niwa_key = os.getenv("NIWA_KEY")
	# niwa_secret = os.getenv("NIWA_SECRET")

	params = {
		"lat": DEFAULT_LOCATION["lat"],
		"long": DEFAULT_LOCATION["long"]
	}

	headers = {
		"x-apikey": niwa_key,
		"Accept": "application/json"
	}

	try:
		r = requests.get(NIWA_API_URL, headers=headers, params=params)
		r.raise_for_status()
		payload = r.json()
		# print(payload)

		products = payload.get("products", [])

		# Find both products
		clear_sky_product = None
		cloudy_sky_product = None

		for product in products:
			if product.get("name") == "clear_sky_uv_index":
				clear_sky_product = product
			elif product.get("name") == "cloudy_sky_uv_index":
				cloudy_sky_product = product

		# Extract max values for both products
		clear_sky_max = extract_max_uv_value(clear_sky_product)
		cloudy_sky_max = extract_max_uv_value(cloudy_sky_product)

		return {
			"clear_sky_max": clear_sky_max, "cloudy_sky_max": cloudy_sky_max
		}

	except Exception as e:
		print(f"Error fetching UV data: {e}")
		return {
			"clear_sky_max": None, "cloudy_sky_max": None
		}
