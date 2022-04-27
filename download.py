from multiprocessing import cpu_count
from multiprocessing.dummy import Pool
from itertools import repeat
import yt_dlp
import time

OPTS = {
    # keep formats as mp4 and m4a
    "AUDIO": {
        'format': "140/bestaudio",
        'outtmpl': "temp/%(id)s.%(ext)s",
        'keepvideo': False
    },
    "VIDEO": {
        'format': "137+140/bestvideo[ext=mp4]+bestaudio[ext=m4a]",
        'outtmpl': "temp/%(id)s.%(ext)s",
        'keepvideo': False
    }
}

def dl_worker(url: str, fmt: str):
    """Downloads video from YouTube as given format

    Args:
        url (str): video url string
        fmt (str): "a" for audio or "v" for video
    """
    ydl_opts = OPTS["VIDEO"] if fmt == "v" else OPTS["AUDIO"]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

def dl_handler(video_urls: [], fmt: str):
    """Iterates through list and runs dl_worker() on multiple threads

    Args:
        video_urls (list): a list of video url strings
        fmt (str): "a" for audio or "v" for video
    """
    start = time.time()
    thread_count = cpu_count()//2
    print(f"RUNNING ON {thread_count} threads")

    # TODO
    #   optimize resource usage
    pool = Pool(thread_count)
    pool.starmap(dl_worker, zip(video_urls, repeat(fmt)))
    pool.close()
    pool.join()

    # bandaid fix for bad resource management
    # dl_worker(list, fmt)
    
    print(f"DOWNLOADS FINISHED in {time.time()-start}s")