from fastapi import FastAPI, Request, HTTPException
import httpx
import asyncio
from geopy.geocoders import Nominatim


app = FastAPI()
API_KEY = "api-key"

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",

    45: "Fog",
    48: "Depositing rime fog",

    51: "Drizzle (light)",
    53: "Drizzle (moderate)",
    55: "Drizzle (dense)",

    56: "Freezing drizzle (light)",
    57: "Freezing drizzle (dense)",

    61: "Rain (slight)",
    63: "Rain (moderate)",
    65: "Rain (heavy)",

    66: "Freezing rain (light)",
    67: "Freezing rain (heavy)",

    71: "Snowfall (slight)",
    73: "Snowfall (moderate)",
    75: "Snowfall (heavy)",

    77: "Snow grains",

    80: "Rain showers (slight)",
    81: "Rain showers (moderate)",
    82: "Rain showers (violent)",

    85: "Snow showers (slight)",
    86: "Snow showers (heavy)",

    95: "Thunderstorm (slight/moderate)",
    96: "Thunderstorm with hail (slight)",
    99: "Thunderstorm with hail (heavy)",
}

async def get_location_name(lat, lon):
    geolocator = Nominatim(user_agent="weather_api")

    # Run blocking reverse-geocode in a thread
    location = await asyncio.to_thread(
        geolocator.reverse,
        (lat, lon),
        language="en"
    )

    if location is None:
        return "Unknown", "Unknown"

    address = location.raw.get("address", {})

    city = (
        address.get("city")
        or address.get("town")
        or address.get("state_district")
        or address.get("village")
        or address.get("hamlet")
    )

    country = address.get("country")

    return city, country

async def get_ip_location(ip):
    url = "https://api.ipgeolocation.io/v2/ipgeo"
    params = {
        "apiKey": API_KEY,
        "ip": ip
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params)
        data = response.json()
        return data

async def get_weather_from_openmeteo(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "rain,temperature_2m,relative_humidity_2m,weather_code,cloud_cover,wind_speed_10m,snowfall,showers,precipitation"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, params=params)
            data = response.json()
            return data
        except:
            return None


@app.get("/weather")
async def get_weather(request:Request,lat:float=None,lon:float=None):

    location_method = "coordinates"
    message = "null"

    if (lat is None) and (lon is None):
        location_method="ip_based"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0]
        else:
            ip = request.client.host
        location_json = await get_ip_location(ip)
        message= f"Location determined from IP address: {ip}"
        lon = location_json['location']['longitude']
        lat = location_json['location']['latitude']
        city = location_json['location']['city']
        country = location_json['location']['country_name']

    elif lat and (lon is None) or lon and (lat is None):
        raise HTTPException(status_code=400, detail={
        "error": "Invalid coordinates provided",
        "code": "INVALID_COORDINATES"
    })

    elif(lat>90) or (lat<-90) or (lon>180) or (lon<-180):
        #return 400
        raise HTTPException(status_code=400, detail={
        "error": "Invalid coordinates provided",
        "code": "INVALID_COORDINATES"
    })
    else:
        city, country = await get_location_name(lat, lon)

    weather_data = await get_weather_from_openmeteo(lat,lon)
    if weather_data is None:
        return{
            "error":"Weather api unavailable"
        }
    weather_code = weather_data["current"]["weather_code"]

    return {
        "location": {
            "city": city,
            "country": country,
            "coordinates": {
                "latitude": lat,
                "longitude": lon
            }
        },
        "weather": {
            "temperature": weather_data["current"]['temperature_2m'],
            "temperature_unit": weather_data['current_units']['temperature_2m'],
            "description": WEATHER_CODES.get(weather_code, "Unknown"),
            "humidity": weather_data['current']['relative_humidity_2m'],
            "wind_speed": weather_data['current']['wind_speed_10m'],
            "wind_speed_unit": weather_data['current_units']['wind_speed_10m'],
        },
        "location_method": location_method,
        "message":message
    }
