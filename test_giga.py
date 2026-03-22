import requests
import json

# Читаем токен
with open('giga_token.txt', 'r') as f:
    token = f.read().strip()

url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': f'Bearer {token}'
}

data = {
    "model": "GigaChat",
    "messages": [
        {"role": "user", "content": "Дай 3 коротких совета для улучшения осанки"}
    ],
    "temperature": 0.7,
    "max_tokens": 500
}

response = requests.post(url, headers=headers, json=data, verify=False)

if response.status_code == 200:
    result = response.json()
    print("✅ GigaChat ответил:")
    print(result['choices'][0]['message']['content'])
else:
    print(f"❌ Ошибка: {response.status_code}")
    print(response.text)