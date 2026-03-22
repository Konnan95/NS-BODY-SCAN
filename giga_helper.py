import requests
import json
import os
import time

TOKEN_FILE = 'giga_token.txt'
TOKEN_EXPIRE = 1800  # 30 минут

def get_token():
    """Получить токен из файла"""
    if os.path.exists(TOKEN_FILE):
        # Проверяем время создания файла
        mod_time = os.path.getmtime(TOKEN_FILE)
        if time.time() - mod_time > TOKEN_EXPIRE - 60:  # обновляем за минуту до истечения
            print("⚠️ Токен истекает, обновляем...")
            return None
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    return None

def refresh_token():
    """Обновить токен"""
    import uuid
    import requests
    from config import GIGACHAT_AUTH_KEY
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {GIGACHAT_AUTH_KEY}'
    }
    data = {'scope': 'GIGACHAT_API_PERS'}
    
    response = requests.post(url, headers=headers, data=data, verify=False)
    
    if response.status_code == 200:
        token = response.json().get('access_token')
        with open(TOKEN_FILE, 'w') as f:
            f.write(token)
        print("✅ Токен обновлён")
        return token
    else:
        print(f"❌ Ошибка обновления токена: {response.status_code}")
        return None

def ask_gigachat(prompt, max_tokens=1000):
    """Отправить запрос к GigaChat с автоматическим обновлением токена"""
    token = get_token()
    if not token:
        token = refresh_token()
        if not token:
            return "❌ Не удалось получить токен"
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        "model": "GigaChat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, verify=False)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        elif response.status_code == 401:
            print("⚠️ Токен истёк, обновляем...")
            token = refresh_token()
            if token:
                headers['Authorization'] = f'Bearer {token}'
                response = requests.post(url, headers=headers, json=data, verify=False)
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
            return "❌ Ошибка авторизации после обновления токена"
        else:
            return f"❌ Ошибка API: {response.status_code}"
    except Exception as e:
        return f"❌ Ошибка: {e}"