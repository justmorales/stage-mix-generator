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
    final_vid = vid_utils.generate_mix(offsets, query.url_to_id(audio_url))

if __name__ == "__main__":
    main()