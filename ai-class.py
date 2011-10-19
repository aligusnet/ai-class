
#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Deepak.G.R."
__license__ = 'Public Domain'

"""
usage:
Go to command line and type

python ai-class.py "topic-name"

topic-names can be "Welcome to AI", "Problem Solving"

PS: Python2.6.2 should be installed in your system.

Let me know if you have any problems.
"""

from urllib import *
from urlparse import *
from sgmllib import SGMLParser
import re
import pdb
import sys
import json
from os import *
from json import *
url_youtube = 'http://www.youtube.com/watch?v='
#req_unit = 'problem solving'
#req_unit = 'welcome to AI'
#req_unit = 'probability in AI'

req_unit = sys.argv[1]
quiz_hash = dict();

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
            match = re.search(text, self.req_unit, re.IGNORECASE)
            
            if match and len(text) != 0:
                self.flag = 1
            

def init_quiz_hash():
    print 'STATUS: Initializing quiz_id hash'
    quiz_url = 'http://www.ai-class.com/course/json/filter/QuizQuestion'
    quiz_url = urlopen(quiz_url);
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
			quiz_hash[i] = list ()
		quiz_hash[i].append(v)

    print 'STATUS: quiz_id Initialized.'

def download_video(urls):
    dirname = 'lecture ' + str(req_unit)
    py_path = path.abspath(sys.argv[0])
    py_path = path.dirname(py_path)
    mkdir(dirname)
    chdir(dirname)
    for video_url in urls:
        video_id = parse_qs(urlparse(video_url).query)['v'][0]
        get_vars = parse_qs(unquote(urlopen("http://www.youtube.com/get_video_info?video_id="+video_id).read()))
        title = get_vars['title'][0] + '.flv'
        i = 0
        entries = (get_vars['fmt_list'][0]).split(',')
        for entry in entries:
            match = re.search(r'^45.*', entry)
            if match:
                break;
            i = i + 1;
        if not match:
			#print 'problem'
			continue

        link = get_vars['itag'][i]
        link = re.findall(r'45,url=(.*)', link)[0]

        print '\n-->Downloading, Title: ', title
        urlretrieve(link, title)
		#break;
        """
        for v in get_vars.keys():
            print v, '\n', get_vars[v], '\n\n'
        pdb.set_trace()
        """
    chdir(py_path)

def main():
    
    init_quiz_hash();
    page = urlopen("http://www.ai-class.com/home/")
    htmlSource = page.read()
    parser = UrlLister()
    print 'STATUS: Fetching video urls.'
    parser.feed(htmlSource)
    print 'STATUS: SUCCESS'
    page.close()
    parser.close()
    
    """
    i = 0
    for url in parser.urls:
        print 'url: ', url, '\n'
        i = i + 1
    """
    print 'Number of videos: ', len(parser.urls);
    print 'STATUS: Starting download.'
    download_video(parser.urls)
    print '\n\n*********Download Finished*********'
    
if __name__  == "__main__":
    main()
