import aiohttp
import asyncio
import logging


async def get_dynamic_advice_async(
		uv_index, lat, lon, weather_main, weather_description, session=None
		):
	"""
	Asynchronously get dynamic advice from a local LLM (Ollama).

	Args:
		uv_index (float): UV index value (0-11+)
		lat (float): Latitude coordinate
		lon (float): Longitude coordinate
		weather_main (str): Main weather condition (e.g., "Clear", "Rain")
		weather_description (str): Detailed weather description
		session (aiohttp.ClientSession, optional): Existing aiohttp session.
												   If None, creates a new one.

	Returns:
		str: AI-generated advice formatted with UV Summary, Clothing, and Sun Protection
			 sections, or error message if request fails
	"""
	system_msg = """You are a helpful assistant that gives sun safety advice based on UV index and weather. 
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
Sun Protection: Sunscreen is optional but recommended if outside for long periods."""

	user_msg = f"""Based on the current UV index and weather condition, give brief and practical clothing and sun safety advice.

Input:
- UV Index: {uv_index}
- Weather: {weather_main}, {weather_description}
- Location: Latitude {lat}, Longitude {lon}

Output:"""

	payload = {
		"model":  "openhermes", "system": system_msg, "prompt": user_msg,
		"stream": False, "temperature": 0.2
	}

	# Use the provided session or create a new one with longer timeout for LLM requests
	close_session = session is None
	if session is None:
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
		return "Error connecting to local LLM: Connection failed"
	except asyncio.TimeoutError as timeout_err:
		logging.error(f"Timeout error occurred: {timeout_err}")
		return "Error: LLM request timed out"
	except ValueError as json_err:
		logging.error(f"JSON parsing error: {json_err}")
		return "Error: Invalid JSON received from LLM"
	except Exception as err:
		logging.error(f"Unexpected error occurred: {err}")
		return f"Error connecting to local LLM: {err}"

	finally:
		# Only close session if we created it
		if close_session:
			await session.close()


def get_dynamic_advice(uv_index, lat, lon, weather_main, weather_description):
	"""
	Synchronous fallback version for getting dynamic advice from local LLM.

	Used as a backup when async version fails or in sync contexts.

	Args:
		uv_index (float): UV index value (0-11+)
		lat (float): Latitude coordinate
		lon (float): Longitude coordinate
		weather_main (str): Main weather condition
		weather_description (str): Detailed weather description

	Returns:
		str: AI-generated advice or error message if request fails
	"""
	import requests

	system_msg = """You are a helpful assistant that gives sun safety advice based on UV index and weather. 
Format your responses like this:

UV Summary: <brief UV risk level>
Clothing: <short clothing advice>
Sun Protection: <short sunscreen and shade advice>"""

	user_msg = f"""Based on the current UV index and weather condition, give brief and practical clothing and sun safety advice.

Input:
- UV Index: {uv_index}
- Weather: {weather_main}, {weather_description}
- Location: Latitude {lat}, Longitude {lon}

Output:"""

	payload = {
		"model":  "openhermes", "system": system_msg, "prompt": user_msg,
		"stream": False, "temperature": 0.2
	}

	try:
		response = requests.post(
				"http://localhost:11434/api/generate", json=payload, timeout=20
		)
		response.raise_for_status()
		data = response.json()
		return data.get('response', 'No advice returned.')

	except requests.exceptions.RequestException as e:
		logging.error(f"Request error: {e}")
		return f"Error connecting to local LLM: {e}"
	except ValueError as e:
		logging.error(f"JSON parsing error: {e}")
		return "Error: Invalid JSON received from LLM"
