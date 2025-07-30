
import requests


def get_dynamic_advice(uv_index, lat, lon, weather_main, weather_description):
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
            "http://localhost:11434/api/generate",
            json={
                "model": "openhermes",
                "system": system_msg,
                "prompt": user_msg,
                "stream": False,
                "temperature": 0.2
            },
            timeout=20
        )
        response.raise_for_status()
        data = response.json()
        # print("Raw Ollama Response:", data)
        return data.get('response', 'No advice returned.')
    except requests.exceptions.RequestException as e:
        return f"Error connecting to local LLM: {e}"
    except ValueError:
        return "Error: Invalid JSON received from LLM."


