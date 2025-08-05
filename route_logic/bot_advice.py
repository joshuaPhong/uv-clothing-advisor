import aiohttp
import asyncio
import logging


async def get_dynamic_advice_async(
		uv_index, lat, lon, weather_main, weather_description, session=None
		):
	"""
    Asynchronously get dynamic advice from local LLM (Ollama).

    Args:
        uv_index: UV index value
        lat: Latitude
        lon: Longitude
        weather_main: Main weather condition
        weather_description: Detailed weather description
        session: Optional aiohttp session. If None, creates a new one.

    Returns:
        String: AI-generated advice or error message
    """
	system_msg = ("""
You are a helpful assistant that gives sun safety advice based on UV index and weather. 
Format your responses like this:

UV Summary: <brief UV risk level>
Clothing: <short clothing advice>
Sun Protection: <short sunscreen and shade advice>

Examples:

Input:
- UV Index: 5.5
- Weather: Sunny
- Location: Latitude -36.85, Longitude 174.76
Output:
UV Summary: Moderate UV risk.
Clothing: Wear a wide-brimmed hat and lightweight, long-sleeved clothing.
Sun Protection: Apply broad-spectrum sunscreen SPF 30+, reapply every 2 hours.

Input:
- UV Index: 1.2
- Weather: Cloudy
- Location: Latitude -36.85, Longitude 174.76
Output:
UV Summary: Low UV risk.
Clothing: Wear a hat and comfortable, light-colored clothing.
Sun Protection: Sunscreen is optional but recommended if outside for long periods.
""")

	user_msg = f"""
Based on the current UV index and weather condition, give brief and practical clothing and sun safety advice.

Input:
- UV Index: 5.5
- Weather: Sunny
- Location: Latitude -36.85, Longitude 174.76

Output:
UV Summary: Moderate UV risk.
Clothing: Wear a wide-brimmed hat and lightweight, long-sleeved clothing.
Sun Protection: Apply broad-spectrum sunscreen SPF 30+, reapply every 2 hours.

---

Input:
- UV Index: 1.2
- Weather: Cloudy
- Location: Latitude -36.85, Longitude 174.76

Output:
UV Summary: Low UV risk.
Clothing: Wear a hat and comfortable, light-colored clothing.
Sun Protection: Sunscreen is optional but recommended if outside for long periods.

---

Input:
- UV Index: {uv_index}
- Weather: {weather_main}, {weather_description}
- Location: Latitude {lat}, Longitude {lon}

Output:
"""

	payload = {
		"model":  "openhermes", "system": system_msg, "prompt": user_msg,
		"stream": False, "temperature": 0.2
	}

	# Use provided session or create a new one
	close_session = session is None
	if session is None:
		# Set longer timeout for LLM requests
		timeout = aiohttp.ClientTimeout(total=30)
		session = aiohttp.ClientSession(timeout=timeout)

	try:
		async with session.post(
				"http://localhost:11434/api/generate", json=payload
		) as response:
			response.raise_for_status()
			data = await response.json()
			return data.get('response', 'No advice returned.')

	except aiohttp.ClientResponseError as http_err:
		logging.error(
			f"HTTP error occurred: {http_err}. Status: {http_err.status}"
			)
		return f"Error connecting to local LLM: HTTP {http_err.status}"
	except aiohttp.ClientConnectionError as conn_err:
		logging.error(f"Connection error occurred: {conn_err}")
		return f"Error connecting to local LLM: Connection failed"
	except asyncio.TimeoutError as timeout_err:
		logging.error(f"Timeout error occurred: {timeout_err}")
		return "Error: LLM request timed out"
	except ValueError as json_err:
		logging.error(f"JSON parsing error: {json_err}")
		return "Error: Invalid JSON received from LLM."
	except Exception as err:
		logging.error(f"Unexpected error occurred: {err}")
		return f"Error connecting to local LLM: {err}"

	finally:
		# Only close session if we created it
		if close_session:
			await session.close()


# Keep the original sync version for backward compatibility
def get_dynamic_advice(uv_index, lat, lon, weather_main, weather_description):
	"""
    Original synchronous version - kept for backward compatibility
    """
	import requests

	system_msg = ("""
You are a helpful assistant that gives sun safety advice based on UV index and weather. 
Format your responses like this:

UV Summary: <brief UV risk level>
Clothing: <short clothing advice>
Sun Protection: <short sunscreen and shade advice>

Examples:

Input:
- UV Index: 5.5
- Weather: Sunny
- Location: Latitude -36.85, Longitude 174.76
Output:
UV Summary: Moderate UV risk.
Clothing: Wear a wide-brimmed hat and lightweight, long-sleeved clothing.
Sun Protection: Apply broad-spectrum sunscreen SPF 30+, reapply every 2 hours.

Input:
- UV Index: 1.2
- Weather: Cloudy
- Location: Latitude -36.85, Longitude 174.76
Output:
UV Summary: Low UV risk.
Clothing: Wear a hat and comfortable, light-colored clothing.
Sun Protection: Sunscreen is optional but recommended if outside for long periods.
"""

	              )
	user_msg = f"""
Based on the current UV index and weather condition, give brief and practical clothing and sun safety advice.

Input:
- UV Index: 5.5
- Weather: Sunny
- Location: Latitude -36.85, Longitude 174.76

Output:
UV Summary: Moderate UV risk.
Clothing: Wear a wide-brimmed hat and lightweight, long-sleeved clothing.
Sun Protection: Apply broad-spectrum sunscreen SPF 30+, reapply every 2 hours.

---

Input:
- UV Index: 1.2
- Weather: Cloudy
- Location: Latitude -36.85, Longitude 174.76

Output:
UV Summary: Low UV risk.
Clothing: Wear a hat and comfortable, light-colored clothing.
Sun Protection: Sunscreen is optional but recommended if outside for long periods.

---

Input:
- UV Index: {uv_index}
- Weather: {weather_main}, {weather_description}
- Location: Latitude {lat}, Longitude {lon}

Output:
"""

	try:
		response = requests.post(
				"http://localhost:11434/api/generate", json={
					"model":  "openhermes", "system": system_msg,
					"prompt": user_msg, "stream": False, "temperature": 0.2
				}, timeout=20
		)
		response.raise_for_status()
		data = response.json()
		return data.get('response', 'No advice returned.')
	except requests.exceptions.RequestException as e:
		return f"Error connecting to local LLM: {e}"
	except ValueError:
		return "Error: Invalid JSON received from LLM."


# Example usage functions
async def main_single():
	"""Example: Single async advice request"""
	print("Getting AI advice asynchronously...")
	advice = await get_dynamic_advice_async(
			uv_index=6.2, lat=-36.8485, lon=174.7633, weather_main="Clear",
			weather_description="clear sky"
	)
	print(f"AI Advice:\n{advice}")


async def main_with_session():
	"""Example: Multiple requests with shared session"""
	async with aiohttp.ClientSession(
			timeout=aiohttp.ClientTimeout(total=30)
			) as session:
		print("Making multiple AI requests with shared session...")

		tasks = [get_dynamic_advice_async(
			6.2, -36.8485, 174.7633, "Clear", "clear sky", session
			), get_dynamic_advice_async(
			2.1, -41.2865, 174.7762, "Clouds", "overcast clouds", session
			)]

		results = await asyncio.gather(*tasks, return_exceptions=True)

		for i, result in enumerate(results):
			if isinstance(result, Exception):
				print(f"Request {i + 1} error: {result}")
			else:
				print(f"Request {i + 1} result:\n{result}\n")


if __name__ == "__main__":
	# Test single async request
	asyncio.run(main_single())

	# Test multiple requests with session reuse  # asyncio.run(main_with_session())