import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

city = "Krasnodar"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    with open("weather.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print("Success")
else:
    print(f"Error: {response.status_code}")