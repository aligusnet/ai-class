#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Deepak.G.R."
__license__ = 'Public Domain'

"""
usage:
Go to command line and type

python ai-class.py "topic-name"

topic-names can be "Welcome to AI", "Problem Solving"

PS: Python 2.7.2 should be installed in your system.

Let me know if you get into any problems.
"""

from urllib import *
from urlparse import *
from sgmllib import SGMLParser
from os import *
from json import *
import re
import pdb
import sys
import json
import urllib2

code = 35
"""
code = 34 for 640*360
code = 35 for 854*480(Default)
code = 22 for 1270*720
"""
if code == 22:
    video_fmt = '.mp4'
else:
    video_fmt = '.flv'
        

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
            text = re.sub(r'[^A-Za-z]', '', text)
            self.req_unit = re.sub(r'[^A-Za-z]', '', self.req_unit)
            match = re.match(text, self.req_unit, re.IGNORECASE)
            if match and len(text) != 0:
                self.flag = 1
            

def init_quiz_hash():
    print 'STATUS: Initializing quiz_id hash'
    quiz_url = 'http://www.ai-class.com/course/json/filter/QuizQuestion'
    quiz_url = urllib2.urlopen(quiz_url);
    data = json.load(quiz_url)
    quiz_id = list()

    for ind in xrange(len(data['data'])):
        piece = str(data['data'][ind])
        match = re.findall('\'youtube_id\': u\'(.+?)\',.*?\'quiz_question\': (\d+?),', piece)
        
        if match:
            for entry in match:
                quiz_id.append(entry)

    
    for v, i in quiz_id:
        if not quiz_hash.has_key(i):
            quiz_hash[i] = list()

        quiz_hash[i].append(v)

    print 'STATUS: quiz_id Initialized.'

def download_video(urls):
    dirname = str(req_unit)
    py_path = path.abspath(sys.argv[0])
    py_path = path.dirname(py_path)
    mkdir(dirname)
    chdir(dirname)
    for video_url in urls:
        video_id = parse_qs(urlparse(video_url).query)['v'][0]
        get_vars = parse_qs(unquote(urlopen("http://www.youtube.com/get_video_info?video_id=" + video_id).read()))
        title = get_vars['title'][0] + video_fmt
        i = 0
        
        entries = get_vars['itag']
        for entry in entries:
            match = re.search(r'.*itag=' + str(code), entry)
            if match:
                break
            i = i + 1
            
        if not match:
            print 'ERROR: Couldn\'t Download video: ', title
            continue

        link = get_vars['itag'][i]
        link = re.findall(r'\d+,url=(.*)', link)[0]

        print '\n-->Downloading, Title: ', title
        
        urlretrieve(link, title)

    chdir(py_path)

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
