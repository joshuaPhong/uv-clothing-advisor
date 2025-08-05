import os
import asyncio
import aiohttp
from typing import Dict, Optional

DEFAULT_LOCATION = {"lat": -36.8485, "long": 174.7633}
NIWA_API_URL = "https://api.niwa.co.nz/uv/data"


def extract_max_uv_value(product):
	"""Helper function to extract max UV value from a product."""
	if not product or "values" not in product:
		return None

	uv_values = [entry["value"] for entry in product["values"] if
	             entry.get("value") is not None and entry.get("value") > 0]

	return max(uv_values) if uv_values else None


async def get_uv_data(session: Optional[aiohttp.ClientSession] = None) -> Dict[
	str, Optional[float]]:
	"""
	Asynchronously fetch UV data from NIWA API.

	Args:
		session: Optional aiohttp session. If None, creates a new one.

	Returns:
		Dictionary with clear_sky_max and cloudy_sky_max UV values
	"""
	niwa_key = os.getenv("NIWA_KEY")

	params = {
		"lat": DEFAULT_LOCATION["lat"], "long": DEFAULT_LOCATION["long"]
	}

	headers = {
		"x-apikey": niwa_key, "Accept": "application/json"
	}

	# Use provided session or create a new one
	close_session = session is None
	if session is None:
		session = aiohttp.ClientSession()

	try:
		async with session.get(
				NIWA_API_URL, headers=headers, params=params
				) as response:
			response.raise_for_status()
			payload = await response.json()

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
	finally:
		# Only close session if we created it
		if close_session:
			await session.close()


async def get_multiple_uv_data(
		locations: list = None, concurrent_limit: int = 5
		) -> list:
	"""
	Fetch UV data for multiple locations concurrently.

	Args:
		locations: List of location dicts with 'lat' and 'long' keys
		concurrent_limit: Maximum number of concurrent requests

	Returns:
		List of UV data results
	"""
	if locations is None:
		locations = [DEFAULT_LOCATION]

	# Create a semaphore to limit concurrent requests
	semaphore = asyncio.Semaphore(concurrent_limit)

	async def fetch_location_data(session, location):
		async with semaphore:
			# Temporarily modify the global location for this request
			original_location = DEFAULT_LOCATION.copy()
			DEFAULT_LOCATION.update(location)
			try:
				result = await get_uv_data(session)
				result['location'] = location
				return result
			finally:
				DEFAULT_LOCATION.update(original_location)

	async with aiohttp.ClientSession() as session:
		tasks = [fetch_location_data(session, loc) for loc in locations]
		results = await asyncio.gather(*tasks, return_exceptions=True)

		# Handle any exceptions
		processed_results = []
		for i, result in enumerate(results):
			if isinstance(result, Exception):
				print(f"Error for location {locations[i]}: {result}")
				processed_results.append(
						{
							"clear_sky_max": None, "cloudy_sky_max": None,
							"location":      locations[i], "error": str(result)
						}
				)
			else:
				processed_results.append(result)

		return processed_results


# Example usage functions
async def main_single():
	"""Example: Single async request"""
	print("Fetching UV data asynchronously...")
	uv_data = await get_uv_data()
	print(f"UV Data: {uv_data}")


async def main_multiple():
	"""Example: Multiple concurrent requests"""
	locations = [{"lat": -36.8485, "long": 174.7633},  # Auckland
		{"lat": -41.2865, "long": 174.7762},  # Wellington
		{"lat": -43.5321, "long": 172.6362},  # Christchurch
	]

	print("Fetching UV data for multiple locations...")
	results = await get_multiple_uv_data(locations)

	for result in results:
		location = result.get('location', {})
		print(
			f"Location ({location.get('lat')}, {location.get('long')}): "
			f"Clear sky: {result.get('clear_sky_max')}, "
			f"Cloudy sky: {result.get('cloudy_sky_max')}"
			)


async def main_with_session_reuse():
	"""Example: Reusing session for multiple calls"""
	async with aiohttp.ClientSession() as session:
		print("Making multiple requests with shared session...")

		# Make multiple requests reusing the same session
		tasks = [get_uv_data(session) for _ in range(3)]
		results = await asyncio.gather(*tasks)

		for i, result in enumerate(results):
			print(f"Request {i + 1}: {result}")


if __name__ == "__main__":
	# Run single request example
	asyncio.run(main_single())

# Run multiple locations example  # asyncio.run(main_multiple())

# Run session reuse example  # asyncio.run(main_with_session_reuse())