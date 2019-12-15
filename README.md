# detect-intros-from-video

## To start
- git clone https://github.com/JacobEkedahl/detect-intros-from-video
- cd detect-intros-from-video
- pip install -r requirements.txt

## Run svtplaydownloader:
- python main.py --dlv --url "url from svt video"

## Run Scene Detector:
- python main.py --seg
- python main.py --seg temp/myvideo.mp4

## Run downloader and segmentor at once
- Move the file of all videos to download under temp/ in root called video-serier.txt
- python main.py --start

## Extra
- Run command from root folder (same directory as lib, src exists)
- All video files will be stored inside temp/videos

