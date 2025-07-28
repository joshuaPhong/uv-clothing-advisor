from flask import Flask, render_template
import requests
import requests.auth
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

NIWA_KEY = os.getenv("NIWA_KEY")
NIWA_SECRET = os.getenv("NIWA_SECRET")
NIWA_API_URL = "https://api.niwa.co.nz/uv/data"

DEFAULT_LOCATION = {"lat": -36.8485, "long": 174.7633}


def get_clothing_advice(uv_index):
	if uv_index is None:
		return "UV data unavailable."
	if uv_index <= 2:
		return "Low UV: Light clothing, no hat needed."
	elif uv_index <= 5:
		return "Moderate UV: Cover shoulders, wear a hat."
	elif uv_index <= 7:
		return "High UV: Hat, sunglasses, long sleeves."
	elif uv_index <= 10:
		return "Very High UV: Avoid midday sun, full coverage."
	else:
		return "Extreme UV: Stay indoors if possible."


@app.route("/")
def index():
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

		advice = get_clothing_advice(uv_max)

	except Exception as e:
		uv_max = None
		advice = f"Could not fetch UV data: {e}"

	return render_template(
			"index.html", uv_index=uv_max, advice=advice
	)


if __name__ == "__main__":
	app.run(debug=True)