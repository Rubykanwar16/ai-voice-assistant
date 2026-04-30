import json
import os

import requests

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

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


def get_weather_description(code: int) -> str:
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown weather")

def get_weather(city: str) -> str:
    try:
        # Step 1: Geocoding
        geo_resp = requests.get(GEO_URL, params={
            "name": city,
            "count": 1
        }, timeout=5)
        geo_data = geo_resp.json()
        
        if not geo_data.get("results"):
            return f"Could not find coordinates for city '{city}'."
            
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        city_name = location["name"]
        country = location.get("country", "")
        
        # Step 2: Weather Forecast
        weather_resp = requests.get(WEATHER_URL, params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "wind_speed_unit": "ms"
        }, timeout=5)
        weather_data = weather_resp.json()
        
        current = weather_data.get("current", {})
        temp = current.get("temperature_2m", "N/A")
        feels_like = current.get("apparent_temperature", "N/A")
        humidity = current.get("relative_humidity_2m", "N/A")
        wind_speed = current.get("wind_speed_10m", "N/A")
        code = current.get("weather_code", -1)
        
        description = get_weather_description(code)
        
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
