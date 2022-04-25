from query_utils import QueryObject
from scenedetect.frame_timecode import FrameTimecode
import download
import mix_gen
import pprint
import urllib.parse as parse
import os.path as path

DIR = path.dirname(path.abspath(__file__))

def main():
    artist = str(input("artist: "))
    song = str(input("song: "))

    # maybe work without objects because they lurk in memory
    # turn class into a util class, better practice?
    # also prevents this goofy ahh code
    qobject = QueryObject(song, artist)
    pprint.pprint(qobject.search_video())
    print(qobject.search_audio())

    # manual garbage collection
    qobject.closeDriver()

    # CALL THAT MP DOWNLOAD HANDLER
    download.dl_handler(qobject.video_urls, 'v')
    download.dl_handler(qobject.video_urls, 'a')
    print("downloading audio")
    download.dl_worker(qobject.audio_url, 'a')
    


if __name__ == "__main__":
    scenes = (mix_gen.scene_detect(path.join(DIR,'temp','XmkIPTm7U8A.mp4')))
    corrected_scenes = []
    for i in range(len(scenes)):
        corrected_scenes.append((scenes[i][0].get_timecode(), scenes[i][1].get_timecode()))
    pprint.pprint(corrected_scenes)