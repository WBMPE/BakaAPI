import requests
import os
import sys
from dotenv import load_dotenv, set_key
from pathlib import Path

from flask import jsonify

env_file_path = Path("./data/.env")

if not os.path.exists(env_file_path):
    os.makedirs(os.path.dirname(env_file_path), exist_ok=True)
    open(env_file_path, 'a').close()

load_dotenv(env_file_path)


def response(code, data=None, message=None):
    resp = {
        "code": code,
        "data": data,
        "message": message
    }
    return jsonify(resp), code


def construct_songdata(src, url, name, artist, pic=None, lrc=None, video=None):
    return {
        "src": src,
        "url": url,
        "name": name,
        "artist": artist,
        "pic": pic,
        "lrc": lrc,
        "video": video
    }


# get system environment with error quit
def GetSysEnv(name, fail_exit=True):
    value = os.getenv(name)
    if not value:
        if fail_exit:
            print(f"ERROR: Environment variable {name} is not detected!")
            val = input("Please enter the variable's value: ")
            if not val or val == "":
                sys.exit(2)

            SetSysEnv(name, val)
            return val
        return None
    return value


def SetSysEnv(name, value):
    set_key(dotenv_path=env_file_path, key_to_set=name, value_to_set=value)


def get_final_url(url):
    # Make a POST request
    response = requests.get(url)

    # Get the final URL after redirects
    final_url = response.url
    return final_url
