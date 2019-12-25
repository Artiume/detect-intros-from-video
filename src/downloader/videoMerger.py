import os
import re
import subprocess
from glob import glob

import imageio_ffmpeg as ffmpeg

import utils.file_handler as file_handler


def mergeImageAndAudio():
    files = file_handler.get_all_unmerged_files()
    file_names = []
    for file in files:
        print(file.audioName + " : " + file.videoName)
        output = file.fileName + "-converted.mp4"
        command = [ffmpeg._utils.get_ffmpeg_exe(), "-i", file.audioName, "-i", file.videoName, "-c", "copy", "-t", "00:08:00.0", "-y", output]
        subprocess.check_call(command, shell=True) 
        os.remove(file.audioName)
        os.remove(file.videoName)
        file_names.append(output)
    return file_names[0] #return just the first one atm
