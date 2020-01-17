"""
    Commands:

    * --seg -stats     
        Loops through all annotated data creating statistics, includes a optional filter, example: 
        --seg -stats -startfilter lt 1
        --seg -stats -endfilter gt 5

        Requires --seg all has been performed on sufficent amount of videos. 

    * --seg -i temp/videos/video.mp4 
        Detects all scenes for input video.

    * --seg -all
        Applies scenedetection on all videos under temp/ that hasn't been processed previously. 

    * --seg -all -force
        Applies scenedetection on all videos under temp/ regardless of if they have been processed previously. 
"""

import os 
import json 
import statistics 
import matplotlib 


import utils.args_helper as args_helper
import utils.file_handler as file_handler
import segmenter.scenedetector as scenedetector
import db.video_repo as video_repo
import utils.time_handler as time_handler

SCENEDETECT_STATS_FILE  = "temp/stats_scendetect.json"
KEY_SCENES              = scenedetector.DATA_KEY

def __segment_all_scendetect(forced):
    count = 0
    files = file_handler.get_all_mp4_files()
    if forced: 
        for file in files: 
            count = count + 1
            scenedetector.detect_scenes(file)
    else:
        for file in files: 
            if not scenedetector.file_has_been_segmented(file): 
                count = count + 1
                scenedetector.detect_scenes(file)
    print("Scendetection was used on %d/%d files." % (count, len(files)))

def __scendetect_entire__dataset():
    for video in video_repo.find_all_with_intro_annotation():
        __segment_scendetect(video[video_repo.FULL_PATH_KEY])
        

def __segment_scendetect(video_file):
    scenedetector.detect_scenes(video_file)

# Compares the scenes with the annotated intro to determine the margin of error between when scene breaks and intro sequence 
def __get_compare_scenes_to_intro(url, scenes, startStr, endStr):
    introStart = startStr
    introEnd = endStr
    firstScene = None 
    lastScene = None 
    found = False 
    print(url)
    print(startStr)
    print(endStr)
    for scene in scenes: 
        print(scene)
        sceneStart = time_handler.timestamp(scene['start'])
        sceneEnd = time_handler.timestamp(scene['end'])
        if sceneStart <= introStart and introStart <= sceneEnd:
            firstScene = scene 
            s1_start = sceneStart 
            s1_end = sceneEnd
            s1_start_diff = abs(s1_start - introStart) 
            s1_end_diff = abs(s1_end - introStart) 
        if sceneStart <= introEnd and introEnd <= sceneEnd:
            lastScene = scene 
            s2_start = sceneStart
            s2_end = sceneEnd
            s2_start_diff = abs(s2_start - introEnd) 
            s2_end_diff = abs(s2_end - introEnd) 
            found = True 
            break  

    if not found:
        return None

    if (s1_start_diff <= s1_end_diff):
        suggestedStartStr = firstScene['start']
        startError = -s1_start_diff/1000
    else:
        suggestedStartStr = firstScene['end']
        startError = s1_end_diff/1000
    if (s2_start_diff <= s2_end_diff):
        suggestedEndStr = lastScene['start']
        endError = -s2_start_diff/1000
    else:
        suggestedEndStr = lastScene['end']
        endError = s2_end_diff/1000
    return {
        'url': url,
        'introStart': startStr,
        'suggestedStart': suggestedStartStr,
        'startError': startError,
        'introEnd': endStr,
        'suggestedEnd': suggestedEndStr,
        'endError': endError,
    }

def __get_scenedetect_intro_stats():
    annotatedVideos = video_repo.find_all_with_intro_annotation()
    hasScenesCount = 0
    data = []
    for video in annotatedVideos:
        # Premature break as part of the dataset is not fully annotated anymore
        if "frals-oss-ifran-ondo" in video[video_repo.SHOW_ID_KEY]:
            break 
        
        try: 
            video_json = file_handler.load_from_video_file(video[video_repo.FULL_PATH_KEY])
        
            if KEY_SCENES in video_json:
                hasScenesCount = hasScenesCount + 1
                
                intro = video[video_repo.INTRO_ANNOTATION_KEY]

                result = __get_compare_scenes_to_intro(video['url'], video_json[KEY_SCENES], intro['start'], intro['end'])
                if result: 
                    print(result)
        except:
            print("Exception")


    exit()

    print("Processed from annotated set: %d/%d\nSegment the remainder to improve the coverage." % (hasScenesCount, len(annotatedVideos)))


def __display_scendetect_stats(startFilter, endFilter):
    includeEntry = True 
    if startFilter != "":
        startFilterValue = float(startFilter.split(" ")[1])
        startFilter = startFilter.split(" ")[0]
    if endFilter != "":
        endFilterValue = float(endFilter.split(" ")[1])
        endFilter = endFilter.split(" ")[0]
    startErrorsAbs = []
    startErrors = []
    endErrors = []
    matchingEntries = 0
    s = "Start\t\tSceneStart\tStartError\tEnd\t\t SceneEnd\tEndError\turl\n"
    with open(SCENEDETECT_STATS_FILE) as json_file:
        entries = json.load(json_file)
        for entry in entries:          
            startErrorAbs = abs(entry['startError'])
            endError = abs(entry['endError'])
            if startFilter != "":
                includeEntry = False 
                if startFilter == "lt" and startErrorAbs < startFilterValue:
                    includeEntry = True 
                if startFilter == "gt" and startErrorAbs > startFilterValue:
                    includeEntry = True 
            if endFilter != "":
                includeEntry = False 
                if endFilter == "lt" and endError < endFilterValue:
                    includeEntry = True 
                if endFilter == "gt" and endError > endFilterValue:
                    includeEntry = True 

            if includeEntry:
                s = s + entry['introStart'] + "\t" + entry['suggestedStart'] + "\t" + ("%f" % entry['startError']) + "\t" + entry['introEnd'] + "\t" + entry['suggestedEnd'] + "\t" + ("%f" % entry['endError']) + "\t" + entry['url'] + "\n"   
                startErrorsAbs.append(startErrorAbs)
                startErrors.append(entry['startError'])
                endErrors.append(endError)
                matchingEntries = matchingEntries + 1

    print(s)
    print("Entries: %d/%d\n" % (matchingEntries, len(entries)))
    if startFilter != "":
        print("Start filter: %s %d" % (startFilter, startFilterValue)) 
    if endFilter != "":
        print("End filter %s %d" % (endFilter, endFilterValue))
    if len(startErrorsAbs) > 1:
        print("Start Error avg:     %f" % statistics.mean(startErrorsAbs))
        print("Start Error median:  %f" % statistics.median(startErrorsAbs))
        print("Start Error stdev:   %f" % statistics.stdev(startErrorsAbs))

        startErrors.sort()

    if len(endErrors) > 1:
        print("End Error avg:       %f" % statistics.mean(endErrors))
        print("End Error median:    %f" % statistics.median(endErrors))
        print("End Error stdev:     %f" % statistics.stdev(endErrors)) 


def execute(argv):

    if args_helper.is_key_present(argv, "-all"):
        if args_helper.is_key_present(argv, "-force"):
            __segment_all_scendetect(True)
        else: 
            __segment_all_scendetect(False)
        return
    file = args_helper.get_value_after_key(argv, "-input", "-i")
    if file != "" and ".mp4" in file: 
        __segment_scendetect(file)
        return 
        
    if args_helper.is_key_present(argv, "-stats"):

        __get_scenedetect_intro_stats()
        

        exit()

        startFilter = ""
        index = args_helper.get_key_index_first(argv, ["-sf", "-startfilter"])
        if index != -1 and index + 2 < len(argv):
            if (argv[index + 1] == "lt"):
                try:
                    f = float(argv[index + 2])
                    startFilter = "lt " + ("%f" % f)
                except:
                    print("Error: less than filter must contain a float or integer")
            elif (argv[index + 1] == "gt"):
                try:
                    f = float(argv[index + 2])
                    startFilter = "gt " + ("%f" % f)
                except:
                    print("Error: greater than filter must contain a float or integer")
        
        endFilter = ""
        index = args_helper.get_key_index_first(argv, ["-ef", "-endfilter"])
        if index != -1 and index + 2 < len(argv):
            if (argv[index + 1] == "lt"):
                try:
                    f = float(argv[index + 2])
                    endFilter = "lt " + ("%f" % f)
                except:
                    print("Error: less than filter must contain a float or integer")
            elif (argv[index + 1] == "gt"):
                try:
                    f = float(argv[index + 2])
                    endFilter = "gt " + ("%f" % f)
                except:
                    print("Error: greater than filter must contain a float or integer")
        __display_scendetect_stats(startFilter, endFilter)
        return 


