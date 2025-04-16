import requests
import json

API_KEY = "c1a9aa5cc23eec4af76c9faff0e386b3"
city = "Shanghai"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    with open("weather2.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print("Success")
else:
    print(f"Error: {response.status_code}")
