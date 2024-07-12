import asyncio
import os
import re
from typing import Any

from flask import url_for
from tqdm import tqdm
import httpx
from bilibili_api import video, HEADERS
import ffmpeg
from urllib.parse import urlparse, unquote
from common import GetSysEnv

audio_path = GetSysEnv("AUDIO_TEMP")

if not os.path.exists(audio_path):
    os.mkdir(audio_path)


def get_BVCode(url):
    # Regular expression pattern to match the BV code
    pattern = r'[\/=]BV([0-9a-zA-Z]+)'

    # Search for the pattern in the URL
    match = re.search(pattern, url)

    # Check if a match was found
    if match:
        bv_code = match.group(1)
        return "BV" + bv_code
    else:
        return None


def check_exists(url):
    name = get_filename(url)
    baseName = "".join(name.split(".")[:-1])
    output_file = os.path.join(audio_path, baseName + ".ogg")
    if os.path.exists(output_file):
        print(f"file {output_file} already exists.")
        return output_file
    return None


def get_filename(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    # Get the last segment of the path (which is the filename)
    filename = path.split('/')[-1]
    # Decode the filename (if it's URL-encoded)
    filename = unquote(filename)
    return filename


async def convert_audio(input_file):
    # Get the bit rate of the input file
    fileName = "".join(os.path.basename(input_file).split(".")[:-1])
    output_file = os.path.join(audio_path, fileName + ".ogg")
    print(f"converting to {output_file}...")

    (
        ffmpeg
        .input(input_file)
        .output(output_file, audio_bitrate=bit_rate, y=None)
        .global_args('-loglevel', 'panic')
        .run()
    )
    os.remove(input_file)
    return output_file


async def download_url(url):
    name = get_filename(url)
    path = os.path.join("temp", name)
    async with httpx.AsyncClient(headers=HEADERS) as sess:
        resp = await sess.get(url)
        length = int(resp.headers.get('content-length', 0))

        with open(path, 'wb') as f:
            pbar = tqdm(total=length, desc=f'Downloading {name}', unit='B', unit_scale=True)
            async for chunk in resp.aiter_bytes(1024):
                if not chunk: break
                f.write(chunk)
                pbar.update(len(chunk))
    return path


async def get_best_audio_url(v: video.Video):
    download_url_data = await v.get_download_url(0)
    # 解析音频下载信息
    detecter = video.VideoDownloadURLDataDetecter(data=download_url_data)
    streams = detecter.detect_all()
    # 获取质量最高的音频
    audio_list = {}
    for stream in streams:
        if isinstance(stream, video.AudioStreamDownloadURL):
            audio_list[stream.audio_quality.value] = stream.url
    best_audio_quality = max(audio_list.keys())
    best_audio = audio_list[best_audio_quality]
    print(f"found best audio quality: {best_audio_quality}")
    return best_audio


async def get_worst_video_url(v: video.Video):
    download_url_data = await v.get_download_url(0)
    # 解析音频下载信息
    detecter = video.VideoDownloadURLDataDetecter(data=download_url_data)
    streams = detecter.detect_all()
    # 获取质量最高的音频
    video_list = {}
    for stream in streams:
        if isinstance(stream, video.VideoStreamDownloadURL):
            video_list[stream.video_quality.value] = stream.url
    worst_video_quality = min(video_list.keys())
    worst_video = video_list[worst_video_quality]
    print(f"found worst video quality: {worst_video_quality}")
    return worst_video


async def to_url(path):
    filename = os.path.basename(path)
    return filename
    # return url_for('serve_file', filename=filename)


async def get_video_info(bvid) -> tuple[Any, Any, str]:
    v = video.Video(bvid=bvid)
    info = await v.get_info()
    name = info["title"]
    cover = info["pic"]
    audio_url = await get_best_audio_url(v)
    exists = check_exists(audio_url)
    video_url = await get_worst_video_url(v)
    print(video_url)
    videoFileName = await download_url(video_url)
    if exists is not None:
        return name, cover, await to_url(exists)
    audioFileName = await download_url(audio_url)
    audioPath = await convert_audio(audioFileName)
    return name, cover, audioPath


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(get_video_info("BV1ux411c7RP"))
