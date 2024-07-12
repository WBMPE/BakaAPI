import os.path

import asyncio
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, send, Namespace

from common import GetSysEnv, get_final_url, response
from mikufans_lib import get_video_info, get_BVCode

app = Flask(__name__)
TEMP_PATH = GetSysEnv("TEMP")
socketio = SocketIO(app)



def get_audio_info(url):
    # Run the async function in the event loop

    try:
        final_url = get_final_url(url)
    except Exception as e:
        return response(400, message=f"Error requesting url {url}: {e}")

    print(final_url)

    if get_BVCode(final_url) is not None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bvid = get_BVCode(final_url)
        info = loop.run_until_complete(get_video_info(bvid))
        return response(200, info)
    return None


@app.route('/')
def index():
    return response(200, message="BakaAPI is running!")


@app.route('/fetch_song', methods=['GET'])
def fetch_song():
    url = request.args.get('url')
    if not url:
        return response(400, message="Missing 'url' parameter")

    info = get_audio_info(url)

    return info


# Route to serve files from the folder
@app.route('/files/<path:filename>')
def serve_file(filename):
    print(filename)
    return send_from_directory(os.path.abspath(TEMP_PATH), filename)


if __name__ == "__main__":
    socketio.run(app, debug=True)
