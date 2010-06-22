# -*- coding: utf-8 -*-

# Copyright (C) 2008-2009 The Tegaki project contributors
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

import os
import itertools

from tegaki.recognizer import Recognizer, RecognizerError
from tegaki.trainer import Trainer, TrainerError

try:
    import zinnia    

    class HangulRecognizer(Recognizer):

        RECOGNIZER_NAME = "hangul"

        def __init__(self):
            Recognizer.__init__(self)
            self._recognizer = zinnia.Recognizer()
            print "Hangul initialized!"

        def open(self, path):
            ret = self._recognizer.open(path) 
            if not ret: raise RecognizerError, "Could not open!"

        #See http://www.bryceboe.com/2006/10/23/line-segment-intersection-algorithm/

        def ccw(self,A,B,C):
          return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

        def intersect(self,A,B,C,D):
          return self.ccw(A,C,D) != self.ccw(B,C,D) and self.ccw(A,B,C) != self.ccw(A,B,D)


        def intersects(self, strokeA,strokeB):
            ret = False
            for i in range(len(strokeA)-1):
                A = strokeA[i]
                B = strokeA[i+1]
              
                for j in range(len(strokeB)-1):
                    C = strokeB[j]
                    D = strokeB[j+1]
                    ret = ret or self.intersect(A,B,C,D)    
            return ret
                    

        def recognize(self, writing, n=10):
            s = zinnia.Character()

            s.set_width(writing.get_width())
            s.set_height(writing.get_height())

            strokes = writing.get_strokes()
            #check for intersections
            num_strokes = []
            for i in range(len(strokes)):
                num_strokes.append([i,strokes[i]])
            strokecombo = itertools.combinations(num_strokes,2)
            jamo = []
            for stroke_tuple in strokecombo: 
                if self.intersects(stroke_tuple[0][1],stroke_tuple[1][1]):
                    print "Intersection on ", stroke_tuple[0][0], stroke_tuple[1][0]
            
            # recognize    
            for i in range(len(strokes)):
                stroke = strokes[i]
                
                for x, y in stroke:
                    s.add(i, x, y)

            result = self._recognizer.classify(s, n+1)
            size = result.size()

            return [(result.value(i), result.score(i)) \
                        for i in range(0, (size - 1))]

    RECOGNIZER_CLASS = HangulRecognizer

    class HangulTrainer(Trainer):

        TRAINER_NAME = "hangul"

        def __init__(self):
            Trainer.__init__(self)

        def train(self, charcol, meta, path=None):
            self._check_meta(meta)

            trainer = zinnia.Trainer()
            zinnia_char = zinnia.Character()

            for set_name in charcol.get_set_list():
                for character in charcol.get_characters(set_name):      
                    if (not zinnia_char.parse(character.to_sexp())):
                        raise TrainerError, zinnia_char.what()
                    else:
                        trainer.add(zinnia_char)

            if not path:
                if "path" in meta:
                    path = meta["path"]
                else:
                    path = os.path.join(os.environ['HOME'], ".tegaki", "models",
                                        "hangul", meta["name"] + ".model")
            else:
                path = os.path.abspath(path)

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            meta_file = path.replace(".model", ".meta")
            if not meta_file.endswith(".meta"): meta_file += ".meta"
            
            trainer.train(path)
            self._write_meta_file(meta, meta_file)

    TRAINER_CLASS = HangulTrainer

except ImportError:
    pass

