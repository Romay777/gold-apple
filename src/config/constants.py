import datetime
import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://tamagotchi.goldapple.ru/api/v1"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    # 'Content-Type': 'application/json',
    'Content-Type': 'multipart/form-data; boundary=--------------------------977423396343503695764683',
    'Authorization': f'Bearer {os.getenv("TOKEN")}',
    'Referer': 'https://tamagotchi.goldapple.ru/',
    'Origin': 'https://tamagotchi.goldapple.ru',
    'Cookie': '_csrf-api=5b87b2a471181ced6a975561a0d45d2a93998fba3f40cccab7c4a0663fc69e1ba%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_csrf-api%22%3Bi%3A1%3Bs%3A32%3A%22-dVovK-LQKf0qhd6Ak4d2AqcJ1-YoLm6%22%3B%7D'
}
AUTH_PARAMS = {
            'access_token': "your_token",
            'emailSigned': 'false',
            'isWeb': 'true',
            'processingStatus': "Found",
            'pushSigned': 'true',
            'share': 'null',
            'smsSigned': 'false',
            'timestamp': int(datetime.datetime.timestamp(datetime.datetime.now())),
            'token': "your_token",
}