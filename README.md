# Example usage of API
1.Using IP-based location:
```bash
curl https://your-deployed-api.com/weather
```
2.Using coordinates:
```bash
curl "https://your-deployed-api.com/weather?lat=40.7128&lon=-74.0060"
```
# Live demo of this api is available at: 
https://weather.hoelab.org/weather

# Set up
1.Change API_KEY variable in main.py, you can get api key from https://ipgeolocation.io

2.Install all libraries from requirements.txt 
```python
pip install -r requirements.txt
```
3.Run the python script
```bash
fastapi run main.py
```

This API returns weather data in the following structured JSON format:
```json
{
 "location": {
 "city": "San Francisco",
 "country": "US",
 "coordinates": {
 "latitude": 37.7749,
 "longitude": -122.4194
 }
 },
 "weather": {
 "temperature": 18.5,
 "temperature_unit": "celsius",
 "description": "Partly cloudy",
 "humidity": 75,
 "wind_speed": 12.5,
 "wind_speed_unit": "km/h"
 },
 "location_method": "ip_based" | "coordinates",
 "message": "Location determined from IP address: 192.168.1.1" | null
}
```
