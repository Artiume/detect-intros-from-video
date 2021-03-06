""" 
    Scrapes svtplay.se for all seasons and episodes belonging to the specified genres and saves them in a db. 
    You can specify one or more genres when using .execute(argv).
    
    Example: 
        argv = ["-g", "serier", "-g", "barn]
        scrapesvt.execute(argv)
"""

from bs4 import BeautifulSoup
import lxml
import requests
import re
import json
import os
import copy
import logging

from db import video_repo, show_repo
from db.video_repo import Video 
from db.show_repo import Show 
from utils import constants

DEBUG = True 
SAVE_TO_DB = constants.SAVE_TO_DB 

SVT_URL = "https://www.svtplay.se"
FILE_DIR = "temp/scraped_urls.txt"


# Writes the url to a file
def scrape_show(show, genre):
    # Extracts all json data from the show.url
    try: 
        data = json.loads(re.findall(r"root\['__svtplay_apollo'\] = (\{.*?\});", requests.get(show.url).text)[0])
    except Exception as err: 
        logging.exception(err)
        logging.error("Failed to scrap data for %s " % show.name)
        return []
    
    urls = []

    video = Video(show.name, "", 0, 0, "", False )
    for element in data:
       # Extracting from metadata 
        if element.startswith('Episode:'):    
            video.title = data[element]['name']
            pos = data[element]['positionInSeason']
            if pos != "":
                try:
                    video.season = int(pos.split("Säsong ")[1].split(" —")[0])
                except:
                    video.season = 0
                try:
                    video.episode = int(pos.split("Avsnitt ")[1])
                except:
                    video.episode = 0
            else:
                video.season = 0
                video.episode = 0

        # Extracting video url if present
        elif element.startswith('$Episode:') and element.endswith('urls'):
            video.url = data[element]['svtplay']
            if video.url != "":
                video.url = SVT_URL + video.url
                if video.season == 0 or video.episode == 0: 
                    arr = video.url.split('-')
                    for i in range(0, len(arr) - 1):
                        if arr[i] == "sasong" and i + 1 < len(arr):
                            video.season = int(arr[i + 1])
                        elif arr[i] == "avsnitt" and i + 1 < len(arr):
                            video.episode = int(arr[i + 1])

                if SAVE_TO_DB: 
                    video_repo.insert(copy.copy(video)) # only videos not saved before get inserted
                if DEBUG:
                    print("fetched: %s" % video.url)
                urls.append(video.url)
                    
            video.url = ""
            video.season = 0
            video.episode = 0
            video.title = ""

    return urls


def scrape_genre(genre, file):
    url = SVT_URL + "/genre/" + genre
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'lxml')

    # grid = Program A-Ö
    grid = soup.find('div', class_='play_flex-grid lp_grid')
    if grid is None: 
        print("Could not find genre: " + genre)
        return

    # Below loop fetches the title and link of all presented shows
    i = 0
    for article in grid.find_all('article', class_='play_content-item play_grid__item'):
        meta = article.find('div', class_='play_content-item__meta')
        title = meta.h2.span.text
        link = meta.a['href']
        show = Show(title, SVT_URL + link)
        if SAVE_TO_DB:
            show_repo.insert(show)
            
        if DEBUG: 
            print("%d: %s, %s %s" % (i, show.name, show.url, show.dirname))
        file.write("\n%d: %s --- %s \n" % (i, show.name, show.url))
        urls = scrape_show(show, genre)
        for url in urls: 
          file.write("%s\n" % url)  
        i = i + 1
    

def scrape_genres(genres):
    file = open(FILE_DIR,"w+")
    for genre in genres: 
        scrape_genre(genre, file)
    file.close()
    return file 
    
