import os
import traceback

from yt_dlp import YoutubeDL

from common import GetSysEnv
from mikufans_lib import to_url

audio_path = GetSysEnv("AUDIO_TEMP")

ydl_opts = {
    'format': 'mp3/bestaudio/best',
    'cookiefile': './cookies.txt',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'ogg'
    }],
    "outtmpl": {
        'default': '%(id)s.%(ext)s',
        'chapter': '%(id)s_%(section_number)03d.%(ext)s',
    },
    'paths': {
        'home': audio_path,
        'temp': "./ ",
    }
}


def print_exception(e):
    print(f"{type(e).__name__}: {str(e)}")
    print("Stack trace:")
    traceback.print_exc()


def get_file_path(id):
    return os.path.join(audio_path, id + '.ogg')


def find_best_thumbnail(thumbnails):
    if not thumbnails or len(thumbnails) == 0:
        return None
    target_height = 500

    closest_thumbnail = None
    smallest_diff = float('inf')

    for thumbnail in thumbnails:
        if 'height' not in thumbnail:
            continue
        diff = abs(thumbnail['height'] - target_height)

        if diff < smallest_diff:
            closest_thumbnail = thumbnail
            smallest_diff = diff

    if closest_thumbnail is None:
        closest_thumbnail = thumbnails[-1]

    if 'url' not in closest_thumbnail:
        return None

    return closest_thumbnail['url']


def get_song_info(url):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            thumb = find_best_thumbnail(info['thumbnails'])
            title = info['title']
            id = info["id"]
            author = info["uploader"]
            path = get_file_path(id)
            return title, thumb, path, author
    except Exception as e:
        print_exception(e)
        return None


if __name__ == '__main__':
    sample_url = "https://soundcloud.com/user-688171120/high-spec-robot?in_system_playlist=personalized-tracks%3A%3Asblzd-lc_022%3A863657656"
    get_song_info(sample_url)
    print(111)
