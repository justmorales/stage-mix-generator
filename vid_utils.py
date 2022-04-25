import scenedetect
from scenedetect import VideoManager, SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.detectors import ContentDetector
from moviepy.editor import VideoFileClip, clips_array
from cvcalib.audiosync import offset
import urllib.parse as parse
import os.path as path

DIR = path.dirname(path.abspath(__file__))
TEMPDIR = path.join(DIR, 'temp')

def get_vid_offsets(qobject):
    video_filenames = []

    # TODO
    #   move this to query file as get_id or somethin
    for url in qobject.video_urls:
        url_data = parse.urlparse(url)
        split_url = parse.parse_qs(url_data.query)
        video_filenames.append(split_url['v'][0])
    audio_filename = parse.parse_qs(parse.urlparse(qobject.audio_url).query)['v'][0]

    # finds the starting times of the song in each stage
    offsets = {}
    for file in video_filenames:
        vid_offset = offset.find_time_offset([f"{audio_filename}.m4a", f"{file}.m4a"], TEMPDIR, [0,0])
        offsets[path.join(TEMPDIR, f"{file}.mp4")] = vid_offset[0]

    return offsets  # ["path to video": (offset tuple)]


# return 2 lists
#   subclips converted to VideoFileClips
#   path to each video used
def subclip_vid(offsets):
    video_subclips = []
    files_used = []

    for video in offsets:
        # TODO
        ## DESPERATE NEED OF OPTIMIZATIONS
        ## adjust for stages that start a little bit into the song
        ## and stages that start extremely late but use snippets of the song in the intro
        ## maybe find a new library? or implement fourier on my own

        # check if the songs in the stages and official audio begin at the same time (NOT GOOD!!!)
        if offsets[video][0] == 0:
            video_subclips.append(VideoFileClip(video).subclip(offsets[video][1]))
            files_used.append(video)

    return video_subclips, files_used

def scene_detect(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=30.0))

    # downscale video for faster processing
    video_manager.set_downscale_factor()

    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    
    return scene_manager.get_scene_list()