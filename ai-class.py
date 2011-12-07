#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Deepak.G.R."
__credits__ = "Alexander Ignatyev"
__license__ = 'Public Domain'

"""
usage:
Go to command line and type

python ai-class.py "topic-name"

topic-names can be "Welcome to AI", "Problem Solving"

PS: Python 2.7.2 should be installed in your system.

Let me know if you get into any problems.
"""
from xml.etree import ElementTree as ET
from urllib import *
from urlparse import *
from sgmllib import SGMLParser
import os
from json import *
import re
import pdb
import sys
import json
import codecs
import urllib2
import youtube

code = youtube.VideoRes.WXGA
"""
code = nHD for 640*360
code = FWVGA for 854*480(Default)
code = WXGA for 1270*720
"""
if code == youtube.VideoRes.WXGA:
    video_fmt = '.mp4'
else:
    video_fmt = '.flv'

# set languages for subtitles;
languages = [] #all languages
# languages = ['en', 'ru']

subtitles_dirname = 'subtitles' #empty for current dir

url_youtube = 'http://www.youtube.com/watch?v='
quiz_hash = dict();

req_unit = sys.argv[1]

class UrlLister(SGMLParser):
    
    def reset(self):
        SGMLParser.reset(self)
        self.urls = []
        self.flag = 0;
        self.req_unit = req_unit;
        self.names = [];
    
    def start_a(self, attrs):
        href = [value for name, value in attrs if name == 'href']
        topic = re.search(r'/course/topic/(\d)+', str(href[0]))
        
        if topic:
            self.flag = 0

        match = re.search(r'/course/video/\w+/\d+$', str(href[0]))
        
        if match and self.flag == 1:
            category = [value for name, value in attrs if name == 'id']
            
            if 'quiz' in category[0]:
                quiz_id = re.findall(r'quiz_(\d+)', category[0])[0]
                video_ids = quiz_hash[quiz_id]
                for video_id in video_ids:
                    link = url_youtube + video_id
                    self.urls.append(link)
            else:
                video_id = re.findall(r'video_\d+_(.+)', category[0])[0]
                link = url_youtube + video_id
                self.urls.append(link)
            
    def handle_data(self, text):
        if self.flag == 0:
            text = text.strip();
            text = re.sub(r'[^A-Za-z]', '', text).lower()
            self.req_unit = re.sub(r'[^A-Za-z]', '', self.req_unit).lower()
            if text == self.req_unit and len(text) != 0:
                self.flag = 1

def init_quiz_hash():
   print 'STATUS: Initializing quiz_id hash'
   quiz_url = 'http://www.ai-class.com/course/json/filter/QuizQuestion'
   quiz_url = urllib2.urlopen(quiz_url);
   data = json.load(quiz_url)
   quiz_id = list()

   for ind in xrange(len(data['data'])):
       piece = str(data['data'][ind])
       match = re.search(r'\'quiz_question\': (\d+?),', piece)
       v_id = re.findall(r'\'youtube_id\': u\'(.+?)\'', piece)

       hw = re.search(r'\'is_homework\': u\'true', piece)
       if match and v_id:
           q_id = match.group(1)

           for v in v_id:
               if not quiz_hash.has_key(q_id):
                   quiz_hash[q_id] = list()

               quiz_hash[q_id].append(v)

   print 'STATUS: quiz_id Initialized.'

def write_subtitle(title, lang, subtitle):
    if subtitles_dirname:
        if not os.path.exists(subtitles_dirname):
            os.mkdir(subtitles_dirname)
        os.chdir(subtitles_dirname)

    with open(title+'_' + lang + '.srt', 'w') as f:
        f.write( codecs.BOM_UTF8 )
        f.write(subtitle.encode('utf-8'))

    if subtitles_dirname:
        os.chdir('..')

def download_video(urls):
    dirname = str(req_unit)
    
    if os.path.exists(dirname):
        delete_recent_video(dirname)
    else:
        os.mkdir(dirname)
        os.chdir(dirname)
    
    for video_url in urls:
        yt = youtube.YouTube(video_url, code)
        title = yt.get_title()
        video_file = title + video_fmt

        if not os.path.isfile(video_file):
            print '\n-->Downloading, Title: ', title
            video = yt.get_video()
            with open(video_file, 'w') as f:
                f.write(video)

        subtitles = yt.get_subtitles()
        if languages:
            for lang in languages:
                if lang in subtitles:
                    write_subtitle(title, lang, subtitles[lang])
        else:
            for (lang, subtitle) in subtitles.items():
                write_subtitle(title, lang, subtitle)

    os.chdir('..')

def delete_recent_video(dirname):
    os.chdir(dirname)
    files = os.listdir('.')
    if not files:
        return
    
    name = ''
    recent = 0
    for fo in files:
        if os.path.isdir(fo):
            continue
        temp = os.stat(fo).st_mtime
        if temp > recent:
            recent = temp
            name = fo
    os.remove(name)


def main():
    init_quiz_hash();
    page = urllib2.urlopen("http://www.ai-class.com/home/")
    htmlSource = page.read()
    parser = UrlLister()
    print 'STATUS: Fetching video urls.'
    parser.feed(htmlSource)
    print 'STATUS: SUCCESS'
    page.close()
    parser.close()
    print 'Number of videos: ', len(parser.urls);
    print 'STATUS: Starting download.'
 
    download_video(parser.urls)
    
    print '\n\n*********Download Finished*********'
    
if __name__  == "__main__":
    main()
