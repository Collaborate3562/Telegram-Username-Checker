from telethon import TelegramClient, sync
from telethon import functions, types
from telethon import errors
from dotenv.main import load_dotenv
import os
import datetime
import configparser
import requests
import time

AVAILABLE, UNAVAILABLE, INVALID, RATELIMIT, ERROR = range(5)

load_dotenv()

config = configparser.ConfigParser()
config.read('config.ini')

API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

client = TelegramClient('validator_session', int(API_ID), API_HASH)
client.start()

def read_file(filename: str) -> list:
    # Open the file in read mode
    with open(filename, 'r') as f:
        # Read the file contents as a list of strings
        lines = f.readlines()

    # Remove newline characters from the end of each line
    lines = [line.strip() for line in lines]

    return lines

def userLookup(account: str) -> int:
    try: 
        result = client(functions.account.CheckUsernameRequest(username=account))
        if result == True:
            return AVAILABLE
        else:
            return UNAVAILABLE
    except errors.FloodWaitError as fW:
        return RATELIMIT
    except errors.UsernameInvalidError as uI:
        return INVALID
    except errors.rpcbaseerrors.BadRequestError as bR:
        return ERROR

def send_message(text) -> any:
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    params = {'chat_id': CHAT_ID, 'text': text}
    response = requests.post(url, data=params)
    return response

def start_check_usernames():
    while True:
        user_list = read_file('users.txt')

        duration = int(config.get('default', 'notify_duration'))
        isTurned = config.get('default', 'notify_message')

        isOn = False
        if isTurned == 'ON':
            isOn = True
        else:
            isOn = False

        for username in user_list:
            res = userLookup(username)
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            if res == AVAILABLE:
                text = f'"{username}" is available'
                response = send_message(text)

                if response.status_code == 200:
                    print(f'[{formatted_time}] {text}')
                else:
                    print(f'Error {response.status_code}: {response.text}')
            elif res == UNAVAILABLE:
                text = f'"{username}" is unavailable'
                print(f'[{formatted_time}] {text}')
            elif res == RATELIMIT:
                text = 'Hit the rate limit, waiting'
            elif res == INVALID:
                text = f'"{username}" is invalid'
                if isOn:
                    response = send_message(text)

                    if response.status_code == 200:
                        print(f'[{formatted_time}] {text}')
                    else:
                        print(f'Error {response.status_code}: {response.text}')
            time.sleep(duration)

        time.sleep(duration)

if __name__ == '__main__':
    print('Starting....')
    start_check_usernames()
