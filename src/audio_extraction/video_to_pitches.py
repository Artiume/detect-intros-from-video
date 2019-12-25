import os
import subprocess

import imageio_ffmpeg as ffmpeg

from utils import constants, file_handler
from utils import object_handler as handler

from . import extract_list_of_pitches as extrator


def convert(video_file_path):
    if not file_handler.does_meta_contain_obj(constants.PITCH_NAME, video_file_path):
        print("there is no pitch obj")
        get_audio_from_video(video_file_path)
    else:
        print("pitch obj already exists")

def get_audio_from_video(video_file_path):
    video_file_path = str(video_file_path)
    base_dir = file_handler.get_dir_for_meta(video_file_path)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    output = os.path.join(base_dir, "audio.wav")
    command = [ffmpeg._utils.get_ffmpeg_exe.__call__(), "-i", video_file_path, "-ab", "160k", "-ac", "1", "-ar", "44100", "-vn", "-y",  output]
    subprocess.call(command, shell=True) 
    dir_to_audio = os.path.dirname(output)
    pitch_sequences = extrator.get_valid_pitches(output)
    handler.save_obj_in_meta(constants.PITCH_NAME, pitch_sequences, video_file_path) # should probably just annotate instead of saving
    os.remove(output)