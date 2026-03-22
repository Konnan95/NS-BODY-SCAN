import requests
import uuid

# Твой Authorization key
AUTH_KEY = "MDE5ZDEwOTAtMWVkMy03NjgxLThmOTEtNDdhYzE5NDlkYzgwOjBlNDIyMzRmLThjNmQtNDFmNS1iMDUyLWQ4OTVjNWM0Y2ZjZQ=="

url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': str(uuid.uuid4()),
    'Authorization': f'Basic {AUTH_KEY}'
}

data = {
    'scope': 'GIGACHAT_API_PERS'
}

response = requests.post(url, headers=headers, data=data, verify=False)

if response.status_code == 200:
    token = response.json().get('access_token')
    print("✅ Токен получен!")
    
    with open('giga_token.txt', 'w') as f:
        f.write(token)
    print("✅ Токен сохранён в giga_token.txt")
else:
    print(f"❌ Ошибка: {response.status_code}")
    print(response.text)