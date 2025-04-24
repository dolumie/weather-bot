import httpx
from decouple import config
async def get_wether(coord):
    TOKEN= config('WEATHER_API_KEY')
    coord["appid"]=TOKEN
    coord["units"]= "metric"
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.openweathermap.org/data/2.5/weather",params=coord)
        return response.json()
        
       