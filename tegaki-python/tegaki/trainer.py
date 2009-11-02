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

import glob
import os
import imp
from cStringIO import StringIO

from tegaki.dictutils import SortedDict

class TrainerError(Exception):
    pass

class Trainer(object):

    def __init__(self):
        pass
   
    @classmethod
    def get_available_trainers(cls):
        if not "available_trainers" in cls.__dict__:
            cls._load_available_trainers()
        return cls.available_trainers

    @classmethod
    def _load_available_trainers(cls):
        cls.available_trainers  = SortedDict()

        currdir = os.path.dirname(os.path.abspath(__file__))

        try:
            # UNIX
            homedir = os.environ['HOME']
        except KeyError:
            # Windows
            homedir = os.environ['USERPROFILE']

        # FIXME: use $prefix defined in setup
        search_path = ["/usr/local/share/tegaki/engines/",
                       "/usr/share/tegaki/engines/",
                       # for Maemo
                       "/media/mmc1/tegaki/engines/",
                       "/media/mmc2/tegaki/engines/",
                       # personal directory
                       os.path.join(homedir, ".tegaki", "engines"),     
                       os.path.join(currdir, "engines")]

        if 'TEGAKI_ENGINE_PATH' in os.environ and \
            os.environ['TEGAKI_ENGINE_PATH'].strip() != "":
            search_path += os.environ['TEGAKI_ENGINE_PATH'].strip().split(":")

        for directory in search_path:
            if not os.path.exists(directory):
                continue

            for f in glob.glob(os.path.join(directory, "*.py")):
                if f.endswith("__init__.py") or f.endswith("setup.py"):
                    continue

                module_name = os.path.basename(f).replace(".py", "")
                module_name += "trainer"
                module = imp.load_source(module_name, f)

                try:
                    name = module.TRAINER_CLASS.TRAINER_NAME
                    cls.available_trainers[name] = module.TRAINER_CLASS
                except AttributeError:
                    pass         

    def set_options(self, options):
        """
        Process trainer/model specific options.
        """
        pass

    # To be implemented by child class
    def train(self, character_collection, meta):
        """
        character_collection: a tegaki.character.CharacterCollection object
        meta: a dictionary containing the following keys
            - name: full name (mandatory)
            - shortname: name with less than 3 characters (mandatory)
            - language: model language (optional)
        path: path to the ouput model
              (if None, the personal directory is assumed)
        """
        raise NotImplementedError

    def _check_meta(self, meta):
        if not meta.has_key("name") or not meta.has_key("shortname"):
            raise TrainerError, "meta must contain a name and a shortname"

    def _write_meta_file(self, meta, meta_file):
        io = StringIO()
        for k,v in meta.items():
            io.write("%s = %s\n" % (k,v))

        if os.path.exists(meta_file):
            f = open(meta_file)
            contents = f.read() 
            f.close()
            # don't rewrite the file if same
            if io.getvalue() == contents:
                return

        f = open(meta_file, "w")
        f.write(io.getvalue())
        f.close()
