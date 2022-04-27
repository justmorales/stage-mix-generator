from pprint import pprint
import os

import query
import download
import vid_utils

DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    artist = str(input("ARTIST: "))
    song = str(input("SONG: "))

    video_urls = query.search_videos(artist, song)
    audio_url = query.search_audio(artist, song)
    query.close_driver()

    download.dl_handler(video_urls, 'v')
    download.dl_handler(video_urls, 'a')
    download.dl_worker(audio_url, 'a')

    offsets = vid_utils.get_vid_offsets(video_urls, audio_url)
    pprint(offsets)
    subclips = vid_utils.subclip_vid(offsets)

def generate_mix(offsets, audio_path):
    # GET FILES
    
    # GET SUBCLIPS FROM OFFSETS

    # LOAD AUDIO
    # CREATE ORDERED LIST OF SCENES
    # ASSEMBLE VIDEO CLIPS
    return


if __name__ == "__main__":
    main()