#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 The Tegaki project contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Contributors to this file:
# - Mathieu Blondel

from tegaki.character import Point, Stroke, Writing, Character, \
                             CharacterCollection, _XmlBase
from math import sqrt                             

class SVG_Point(Point):
    def add(self, point):
        return Point(self.x + point.x, self.y + point.y)

    def subtract(self, point):
        return Point(self.x - point.x, self.y - point.y)

    def dist(self, point):
        return sqrt((point.x - self.x) ** 2 + (point.y - self.y) ** 2)

    def multiply(self, number):
        return Point(self.x * number, self.y * number)

class SVG_M:

    def __init__(self, p1, p2 = Point(0,0)):
        self._p = p1 + p2;

    def to_points(self):
        return []

    def current_cursor(self):
        return self._p

class SVG_C:

    def __init__(self,c1,c2,p,current_cursor):
        self._c1 = c1
        self._c2 = c2
        self._p = p
        self._current_cursor = current_cursor

    def second_point(self):
        return _c2

    def linear_interpolation(self,a,b,factor):
        xr = a.x + ((b.x - a.x) * factor)
        yr = a.y + ((b.y - a.y) * factor)
        return Point(xr,yr)

    def make_curvepoint(self,factor):
        ab = linear_interpolation(self._current_cursor,self._c1,factor)
        bc = linear_interpolation(self._c1,self._c2,factor)
        cd = linear_interpolation(self._c2,self._p,factor)

        abbc = linear_interpolation(ab,bc,factor)
        bccd = linear_interpolation(bc,cd,factor)
        return linear_interpolation(abbc, bccd, factor)

    def length(self,points):
        old_point = self._current_cursor
        length = 0.0
        factor = points

        for i in range(1, points):
            new_point = make_curvepoint(point/factor)
            length += old_point.dist(new_point)
            old_point = new_point

        return length

    def make_curvepoints_array(self, distance):
        result = []
        l = length(20)
        points = l * distance
        factor = points

        for i in range(0, points):
            result.append(make_curvepoint(point / factor))

        return result

    def to_points(self):
        return make_curvepoints_array(0.3)

    def current_cursor(self):
        return self._p









class KanjiVGReader:
    def __init__(self):
        self._charcol = CharacterCollection()
        
    def get_character_collection(self):
        return self._charcol
    
    def read (self, path):
        return
    

    
    

class TomoeXmlDictionaryReader(_XmlBase):

    def __init__(self):
        self._charcol = CharacterCollection()

    def get_character_collection(self):
        return self._charcol

    def _start_element(self, name, attrs):
        self._tag = name

        if self._first_tag:
            self._first_tag = False
            if self._tag != "dictionary":
                raise ValueError, "The very first tag should be <dictionary>"

        if self._tag == "character":
            self._writing = Writing()

        if self._tag == "stroke":
            self._stroke = Stroke()
            
        elif self._tag == "point":
            point = Point()

            for key in ("x", "y", "pressure", "xtilt", "ytilt", "timestamp"):
                if attrs.has_key(key):
                    value = attrs[key].encode("UTF-8")
                    if key in ("pressure", "xtilt", "ytilt"):
                        value = float(value)
                    else:
                        value = int(float(value))
                else:
                    value = None

                setattr(point, key, value)

            self._stroke.append_point(point)

    def _end_element(self, name):
        if name == "character":
            char = Character()
            char.set_utf8(self._utf8)
            char.set_writing(self._writing)
            self._charcol.add_set(self._utf8)
            self._charcol.append_character(self._utf8, char)

            for s in ["_tag", "_stroke"]:
                if s in self.__dict__:
                    del self.__dict__[s]

        if name == "stroke":
            self._writing.append_stroke(self._stroke)
            self._stroke = None

        self._tag = None

    def _char_data(self, data):
        if self._tag == "utf8":
            self._utf8 = data.encode("UTF-8")
        elif self._tag == "width":
            self._writing.set_width(int(data))
        elif self._tag == "height":
            self._writing.set_height(int(data))

def tomoe_dict_to_character_collection(path):
    reader = TomoeXmlDictionaryReader()
    gzip = False; bz2 = False
    if path.endswith(".gz"): gzip = True
    if path.endswith(".bz2"): bz2 = True
    reader.read(path, gzip=gzip, bz2=bz2)
    return reader.get_character_collection()

