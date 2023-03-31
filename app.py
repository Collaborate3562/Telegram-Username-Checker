from telethon import TelegramClient
from telethon.errors.rpcerrorlist import UsernameOccupiedError, UsernameInvalidError
from dotenv.main import load_dotenv
import os
import requests
import threading
import time

load_dotenv()

API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']
BOT_TOKEN = os.environ['BOT_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

client = TelegramClient('validator_session', int(API_ID), API_HASH)

def read_file(filename: str) -> list:
    # Open the file in read mode
    with open(filename, 'r') as f:
        # Read the file contents as a list of strings
        lines = f.readlines()

    # Remove newline characters from the end of each line
    lines = [line.strip() for line in lines]

    return lines

async def check_username(username: str):
    try:
        result = await client.get_entity(username)
        if result.username == username:
            return True  # username already taken
    except UsernameInvalidError:
        return True  # username is available
    except UsernameOccupiedError:
        return True  # username already taken
    except Exception as e:
        print(e)
        return False  # error occurred, assume username is taken

def send_message(text) -> any:
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    params = {'chat_id': CHAT_ID, 'text': text}
    response = requests.post(url, data=params)
    return response

def start_check_usernames():
    while True:
        user_list = read_file('users.txt')
        setting = read_file('config.txt')

        duration = int(setting[0].split('=')[1])
        isOn = False
        if setting[1].split('=')[1] == 'ON':
            isOn = True
        else:
            isOn = False

        for username in user_list:
            with client:
                is_available = client.loop.run_until_complete(check_username(username))
                print(username, is_available)
                print(isOn)
                text = f'The username "{username}" is {"available" if is_available else "unavailable"}'
                if is_available:
                    res = send_message(text)

                    if res.status_code == 200:
                        print('Message sent successfully!')
                    else:
                        print(f'Error {res.status_code}: {res.text}')
                elif not is_available and isOn:
                    res = send_message(text)

                    if res.status_code == 200:
                        print('Message sent successfully!')
                    else:
                        print(f'Error {res.status_code}: {res.text}')

        time.sleep(duration)

if __name__ == '__main__':
    start_check_usernames()
