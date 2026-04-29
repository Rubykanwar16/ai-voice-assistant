import json
import os

import requests

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# Tool definitions passed to Groq
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city. Use this whenever the user asks about weather, temperature, or climate in any city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. Mumbai, Delhi, London, New York"
                    }
                },
                "required": ["city"]
            }
        }
    }
]


def get_weather(city: str) -> str:
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        return "Weather feature is not configured. Please add WEATHER_API_KEY to your .env file."
    try:
        resp = requests.get(WEATHER_URL, params={
            "q": city,
            "appid": api_key,
            "units": "metric"
        }, timeout=5)
        data = resp.json()
        if resp.status_code != 200:
            error_msg = data.get("message", "Unknown error")
            return f"Could not find weather data for '{city}'. Error: {error_msg}"
        temp        = data["main"]["temp"]
        feels_like  = data["main"]["feels_like"]
        humidity    = data["main"]["humidity"]
        description = data["weather"][0]["description"].capitalize()
        wind_speed  = data["wind"]["speed"]
        city_name   = data["name"]
        country     = data["sys"]["country"]
        return (
            f"{city_name}, {country}: {description}. "
            f"Temperature {temp}°C (feels like {feels_like}°C). "
            f"Humidity {humidity}%, wind speed {wind_speed} m/s."
        )
    except requests.exceptions.Timeout:
        return "Weather request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "Could not connect to weather service. Please check your internet connection."
    except Exception as e:
        return f"Could not fetch weather: {str(e)}"


TOOL_MAP = {
    "get_weather": lambda args: get_weather(args.get("city", ""))
}


def execute_tool(name: str, arguments: str) -> str:
    try:
        args = json.loads(arguments)
    except Exception:
        args = {}
    fn = TOOL_MAP.get(name)
    return fn(args) if fn else "Unknown tool called."
