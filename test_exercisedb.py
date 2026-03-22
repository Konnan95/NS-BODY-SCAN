import requests

API_KEY = "f7b1970b4fmshab4a7caadcbb35fp126741jsn27ab090ace7d"
HOST = "exercisedb.p.rapidapi.com"

# Поиск упражнения "pushup"
url = "https://exercisedb.p.rapidapi.com/exercises/name/pushup"

headers = {
    'X-RapidAPI-Key': API_KEY,
    'X-RapidAPI-Host': HOST
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
if response.status_code == 200:
    data = response.json()
    if data:
        print("✅ Найдено упражнений:", len(data))
        print("Название:", data[0].get('name'))
        print("Видео:", data[0].get('videoUrl'))
    else:
        print("❌ Упражнение не найдено")
else:
    print("Ошибка:", response.text)