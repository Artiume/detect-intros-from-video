
import json 

import db.video_repo as video_repo 
import utils.args_helper as args_helper
import annotations.dataset_annotation as dataset_annotation
import utils.time_handler as time_handler



# arguments: -show 'Vår tid är nu' -season 1
def __query_videos(argv):

    episode = args_helper.get_value_after_key(argv, "-episode", "-episode")
    season = args_helper.get_value_after_key(argv, "-season", "-season")
    show = args_helper.get_value_after_key(argv, "-show", "-show")
    displayDetails = args_helper.is_key_present(argv, "-details")
    videos = []
    if show != "":
        if season != "":
            if episode != "":
                videos = video_repo.find_by_show_season_episode(show, int(season), int(episode))
            else:
                videos = video_repo.find_by_show_and_season(show, int(season))
        else:
            videos = video_repo.find_by_show(show)
    else:
        videos = video_repo.find_all()
    for v in videos: 
        if displayDetails: 
            print(v)
        else:
            if v[video_repo.DOWNLOADED_KEY]:
                print("%s s%02de%02d %s %s" % (v[video_repo.SHOW_KEY], v[video_repo.SEASON_KEY], v[video_repo.EPISODE_KEY], v[video_repo.DOWNLOADED_KEY], v[video_repo.FULL_PATH_KEY]))
            else:
                print("%s s%02de%02d %s %s" % (v[video_repo.SHOW_KEY], v[video_repo.SEASON_KEY], v[video_repo.EPISODE_KEY], v[video_repo.DOWNLOADED_KEY]))


def execute(argv):  
     __query_videos(argv) 






