from flask import Flask, render_template
from route_logic.uv_service import get_uv_data
from route_logic.advice import get_clothing_advice

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
	uv_max = get_uv_data()
	if uv_max is None:
		advice = "Could not fetch UV data. Please try again later."
	else:
		advice = get_clothing_advice(uv_max)

	return render_template(
			"index.html", uv_index=uv_max, advice=advice
	)


if __name__ == "__main__":
	app.run(debug=True)
