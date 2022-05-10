from scenedetect import VideoManager, SceneManager, StatsManager, ContentDetector, FrameTimecode
from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips
from cvcalib.audiosync import offset
from query import url_to_id
from secrets import randbelow
import numpy as np
import os

DIR = os.path.dirname(os.path.abspath(__file__))
TEMPDIR = os.path.join(DIR, 'temp')

def get_vid_offsets(video_urls: [str], audio_url: str) -> []:
    """Get audio-video offsets (based on official audio) of downloaded stages

    Args:
        video_urls (list): a list of video url strings
        audio_url (string): video url string

    Returns:
        offsets (list): ['path-to-video': (offset tuple)]
    """

    video_filenames = []
    audio_filename = url_to_id(audio_url)

    for url in video_urls:
        video_filenames.append(url_to_id(url))

    # finds the starting times of the song in each stage
    offsets = {}
    for file in video_filenames:
        vid_offset = offset.find_time_offset([f"{audio_filename}.m4a", f"{file}.m4a"], TEMPDIR, [0,0])
        offsets[os.path.join(TEMPDIR, f"{file}.mp4")] = vid_offset[0]
    return offsets

def subclip_vid(offsets):
    """Cut videos to line up with official audio based on calculated offsets
    
    Args:
        offsets (list): ['path-to-video': (offset tuple)]
    
    Returns:
        video_subclips (list): a list of VideoFileClips
        files_used (list): a list of paths to videos used
    """
    video_subclips = []
    audio_subclips = []
    files_used = []

    for video in offsets: # optimize/fix
        if offsets[video][0] == 0:
            video_subclips.append(VideoFileClip(video).subclip(offsets[video][1]))
            audio_subclips.append(AudioFileClip(f"{video[:-4]}.m4a").subclip(offsets[video][1]))
            files_used.append(video)

    return video_subclips, audio_subclips, files_used

def scene_detect(video_path):
    """Detects scenes in a video
    
    Args:
        video_path (str): path to video
    
    Returns:
        scene_list (list): [(start of scene, end of scene)]
    """
    video_manager = VideoManager([video_path])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    scene_manager.add_detector(ContentDetector(threshold=30.0))

    stats_file_path = f"{video_path}.stats.csv"

    scene_list = []

    try:
        if os.path.exists(stats_file_path):
            with open(stats_file_path, 'r') as stats_file:
                stats_manager.load_from_csv(stats_file)

        # downscale video for faster processing
        video_manager.set_downscale_factor()

        video_manager.start()
        scene_manager.detect_scenes(frame_source=video_manager)

        scene_list = scene_manager.get_scene_list()

        if stats_manager.is_save_required():
            base_timecode = video_manager.get_base_timecode()
            with open(stats_file_path, 'w') as stats_file:
                stats_manager.save_to_csv(stats_file, base_timecode)
    finally:
        # release all cv capture processes MEMORY MANAGEMENT WOO
        video_manager.release()

    return scene_list

def generate_mix(offsets, audio_id):
    # GET FILES

    # GET SUBCLIPS FROM OFFSETS
    v_subclips, a_subclips, video_paths = subclip_vid(offsets)

    # LOAD AUDIO
    audio_path = os.path.join(TEMPDIR, f"{audio_id}.m4a")
    official_audio = AudioFileClip(audio_path)

    # CREATE ORDERED LIST OF SCENES
    clips = []

    scenes = []
    for v in video_paths:
        scenes.append(scene_detect(v))

    curr = 0.0
    while curr < float(official_audio.duration):
        random = randbelow(len(v_subclips))
        print(random)

        if curr > float(v_subclips[random].duration) + 2:
            continue
    
        offset_v = list(offsets.values())
        for i, scene in enumerate(scenes[random]):
            print(scene[1].get_seconds())
            scene_end = scene[1].get_seconds() - offset_v[random][1]
            if scene_end > curr + 1.0 and scene_end < float(official_audio.duration) + 5:
                clips.append(v_subclips[random].subclip(curr, scene_end))
                curr = scene_end
                break

    # ASSEMBLE VIDEO CLIPS
    print(clips)
    final = concatenate_videoclips(clips)
    final = final.set_audio(a_subclips[0])

    mix_path = os.path.join(DIR, "final_mix.mp4")
    final.write_videofile(mix_path, codec='mpeg4', preset='medium', write_logfile=True, threads=3)

    official_audio.reader.close_proc()

    for video in v_subclips:
        video.reader.close()
    
    for audio in a_subclips:
        audio.reader.close_proc()

    return mix_path