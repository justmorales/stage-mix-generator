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

# @param url string
#   url to download
# @param fmt 'v' or 'a'
#   v for video, a for audio
def dl_worker(url, fmt):
    ydl_opts = OPTS["VIDEO"] if fmt == "v" else OPTS["AUDIO"]
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

# @param list []
#   list of urls to download
# @param fmt 'v' or 'a'
#   v for video, a for audio
def dl_handler(list, fmt):
    start = time.time()
    thread_count = cpu_count()
    print(f"RUNNING ON {thread_count//2} threads")

    # TODO
    ## optimize resource usage
    pool = Pool(thread_count//2)
    pool.starmap(dl_worker, zip(list, repeat(fmt)))
    pool.close()
    pool.join()

    # bandaid fix for bad resource management
    # dl_worker(list, fmt)
    
    print(f"DOWNLOADS FINISHED in {time.time()-start}s")