import datetime
import os

from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://tamagotchi.goldapple.ru/api/v1"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {os.getenv("TOKEN")}',
    'Referer': 'https://tamagotchi.goldapple.ru/',
    'Origin': 'https://tamagotchi.goldapple.ru',
}
AUTH_PARAMS = {
            'access_token': "PRFY9pV6OtdCPO_RmayGw4BiWmxCmhzN",
            'emailSigned': 'false',
            'isWeb': 'true',
            'processingStatus': "Found",
            'pushSigned': 'true',
            'share': 'null',
            'smsSigned': 'false',
            'timestamp': int(datetime.datetime.timestamp(datetime.datetime.now())),
            'token': "PRFY9pV6OtdCPO_RmayGw4BiWmxCmhzN",
}