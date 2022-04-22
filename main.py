from query_utils import QueryObject
import download
import pprint
import urllib.parse as parse

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
    main()