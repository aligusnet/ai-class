#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Alexander Ignatyev"
__license__ = 'Public Domain'

from xml.etree import ElementTree

def __time_format(secs):
    hrs = 0
    mins = 0
    parts = str(secs).split('.')
    secs = int(parts[0])
    msecs = parts[1]

    if secs >= 60:
        mins = mins + (secs/60)
        secs = secs % 60

    if mins >= 60:
        hrs = hrs + (mins/60)
        mins = mins % 60

    h = '%02d' % hrs
    m = '%02d' % mins
    s = '%02d' % secs
    ms = msecs + '0' * (3-len(msecs))
    return h + ':' + m + ':' + s + ',' + ms

def convert(xml_data):
    srt_string = ''
    try:
        tree = ElementTree.fromstring(xml_data)
    except:
        return srt_string

    line = 1
    for subelement in tree:
        time = subelement.attrib
        secs = float(time['start'])
        srt_string += str(line) + '\n'
        srt_string += __time_format(secs)
        srt_string += ' --> '
        dur = float(time['dur'])
        secs += dur
        srt_string += __time_format(secs)
        srt_string += '\n' + subelement.text + '\n\n'
        line += 1
    return srt_string
