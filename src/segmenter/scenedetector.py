# ------------------------------------------------------------------------- #
# Implements PySceneDetect to detect scene transitions of a video. Produces #
# a json file containing information about all detected scenes, as well as  #
# a cvs file containing a statistical analysis of all the frames.           #                                            
#                                                                           #
# Example usage 1:                                                          #        
#   py scenedetector.py myvideo.mp4                                         #
#                                                                           # 
# Example usage 2:                                                          # 
#   py scenedetector.py c:/somepath/                                        #
#                                                                           #
# Notice:                                                                   #
# You can either provide a single .mp4 file or a directory. If a full path  # 
# to a directory is provided every single video will be processed           #
#                                                                           #
# ------------------------------------------------------------------------- #

# Source: https://pyscenedetect.readthedocs.io/en/latest/examples/usage-python/

import scenedetect 
import numpy
import cv2
import os 
import sys 
import json 

from scenedetect.video_manager import VideoManager
from scenedetect.scene_manager import SceneManager
from scenedetect.frame_timecode import FrameTimecode
from scenedetect.stats_manager import StatsManager
from scenedetect.detectors import ContentDetector

DEFAULT_START_TIME = 0.0        # 00:00:00.00
DEFAULT_END_TIME = 600.0        # 00:10:00.00

def segment_video(video_file):

    # requires that they all have the same frame size, and optionally, framerate.
    video_manager = VideoManager([video_file])
    stats_manager = StatsManager()
    scene_manager = SceneManager(stats_manager)
    # Add ContentDetector algorithm (constructor takes detector options like threshold).
    scene_manager.add_detector(ContentDetector())
    base_timecode = video_manager.get_base_timecode()

    try:
        # Uses the video file path and replaces .mp4 with another ending
        stats_file_path = video_file.replace('.mp4', '') + '.stats.cvs'
        # If stats file exists, load it.
        if os.path.exists(stats_file_path):
            # Read stats from CSV file opened in read mode:
            with open(stats_file_path, 'r') as stats_file:
                stats_manager.load_from_csv(stats_file, base_timecode)

        start_time = base_timecode + DEFAULT_START_TIME      
        end_time = base_timecode + DEFAULT_END_TIME   
        video_manager.set_duration(start_time=start_time, end_time=end_time)

        # Set downscale factor to improve processing speed (no args means default).
        video_manager.set_downscale_factor()

        video_manager.start()

        # Perform scene detection on video_manager.
        scene_manager.detect_scenes(frame_source=video_manager)

        # Obtain list of detected scenes.
        scene_list = scene_manager.get_scene_list(base_timecode)
        # Like FrameTimecodes, each scene in the scene_list can be sorted if the
        # list of scenes becomes unsorted.

        print('List of scenes obtained from %s:' % video_file)

        json_data = {}
        json_data['scenes'] = []

        for i, scene in enumerate(scene_list):
            json_data['scenes'].append({
                'scene': i + 1,
                'start': scene[0].get_timecode(),
                'startFrame': scene[0].get_frames(),
                'end':  scene[1].get_timecode(),
                'endFrame': scene[1].get_frames(),
                'intro': False
            })
            print('    Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
                i+1,
                scene[0].get_timecode(), scene[0].get_frames(),
                scene[1].get_timecode(), scene[1].get_frames(),))

        with open(video_file.replace('.mp4', '') + '.json', 'w') as outfile:
            json.dump(json_data, outfile)

        # We only write to the stats file if a save is required:
        if stats_manager.is_save_required():
            with open(stats_file_path, 'w') as stats_file:
                stats_manager.save_to_csv(stats_file, base_timecode)

    finally:
        video_manager.release()


def get_all_paths(fullPath):
    files = []
    for file in os.listdir(fullPath):
        if file.endswith(".mp4"):
            files.append(fullPath + file)
    return files


def segment_all_videos_in_dir(target_directory):
    video_files = get_all_paths(target_directory)
    i = 1
    max = len(video_files)
    for video_file in video_files: 
        segment_video(video_file)
        print("segmented %d/%d" % (i, max))
        i = i + 1

if len(sys.argv) - 1 < 1:
    print("No arguments found")
    exit()

if sys.argv[1].endswith(".mp4"):
    segment_video(sys.argv[1])
else:
    segment_all_videos_in_dir(sys.argv[1])
