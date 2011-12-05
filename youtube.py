#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Alexander Ignatyev"
__license__ = 'Public Domain'

from urlparse import urlparse, parse_qs
from urllib import urlopen, urlretrieve, unquote
from xml.etree import ElementTree
from os.path import splitext
import re
import xml2srt

class VideoRes:
    nHD = 34 #640*360
    FWVGA = 35 #854*480
    WXGA = 22 #1280*720

class YouTube:
    VideoInfo='http://www.youtube.com/get_video_info?video_id=%(video_id)s'
    SubtitlesList = 'http://video.google.com/timedtext?hl=%(hl)s&v=%(video_id)s&type=list'
    Subtitle = 'http://video.google.com/timedtext?hl=%(hl)s&v=%(video_id)s&type=track&name=%(track_name)s&lang=%(lang)s'

    def __init__(self, url, code_format):
        self.video_id = parse_qs(urlparse(url).query)['v'][0]
        params = {'video_id': self.video_id}
        self.get_vars = parse_qs(unquote(urlopen(YouTube.VideoInfo % params).read()))
        self.title = splitext(self.get_vars['title'][0])[0]
        self.code_format = code_format

    def get_video(self):
        link = self.__get_video_link()
        if not link:
            return None
        return urlopen(link).read()

    def get_subtitles(self):
        links = self.__get_subtitle_links()
        subtitles = {}
        for (lang, link) in links.items():
            data = urlopen(link).read()
            subtitles[lang] = xml2srt.convert(data)
        return subtitles

    def get_title(self):
        return self.title

    def __get_video_link(self):
        i = 0
        entries = self.get_vars['itag']
        for entry in entries:
            match = re.search(r'.*itag=' + str(self.code_format), entry)
            if match:
                break
            i = i + 1

        if match:
            link = self.get_vars['itag'][i]
            return re.findall(r'\d+,url=(.*)', link)[0]
        else:
            return ''

    def __get_subtitle_links(self):
        params = {'video_id': self.video_id, 'hl': 'en'}
        xml_list = urlopen(YouTube.SubtitlesList % params).read()
        try:
            tree = ElementTree.fromstring(xml_list)
        except:
            print 'ERROR: invalid subtitles list'
            return {}
        subtitle_links = {}
        for subelement in tree:
            track = subelement.attrib
            params['lang'] = track['lang_code']
            params['track_name'] = track['name']
            subtitle_links[track['lang_code']] = YouTube.Subtitle % params
        return subtitle_links


def main():
    #url = 'http://www.youtube.com/watch?v=beb_cF5fcmk'
    url = 'http://www.youtube.com/watch?v=mtbfvJuOV_U'
    yt = YouTube(url, VideoRes.WXGA)
    #yt.download_video()
    subs = yt.get_subtitles()
    print subs['ru']

if __name__ == '__main__':
    main()
