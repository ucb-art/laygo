#!/usr/bin/python
########################################################################################################################
#
# Copyright (c) 2014, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################################################################

"""
The TemplateDB module/class implements template database management functions for GridBaseLayoutGenerator module.
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

from .TemplateObject import *
import yaml
import logging

class TemplateDB(dict):
    """
    layout template database class
    """
    templates = None
    """dict: template dictionary"""
    plib = None
    """str: current library handle"""

    def __init__(self):
        """
        Constructor
        """
        #self.templates = dict()
        self.templates = self

    # aux functions
    def display(self, libname=None, templatename=None):
        """
        Display design database

        Parameters
        ----------
        libname : str, optional
            library name. If None, all libraries are displayed
        templatename : str, optional
            template name. If None, all templates are displayed
        """
        if libname == None:
            libstr = ""
        else:
            libstr = "lib:" + libname + ", "
        if templatename == None:
            templatestr = ""
        else:
            templatestr = "template:" + templatename
        print('Display ' + libstr + templatestr)
        for ln, l in self.items():
            if libname==None or libname==ln:
                print('[Library]' + ln)
                for sn, s in l.items():
                    if templatename==None or templatename==sn:
                        print(' [Template]' + sn)
                        s.display()

    def export_yaml(self, filename, libname=None):
        """
        Export template database to a yaml file

        Parameters
        ----------
        filename : str
            yaml file name
        libname : str, optional
            library name to be exported
        """
        if libname == None:
            libstr = ""
            liblist=self.keys()
        else:
            libstr = "lib:" + libname + ", "
            liblist=[libname]
        # export template
        export_dict = dict()
        print('Export template' + libstr)
        for ln in liblist:
            l=self[ln]
            export_dict[ln] = dict()
            print('[Library]' + ln)
            for sn, s in l.items():
                print(' [Template]' + sn)
                export_dict[ln][sn] = s.export_dict()
        with open(filename, 'w') as stream:
            yaml.dump(export_dict, stream)

    def import_yaml(self, filename, libname=None):
        """
        Import template database from an external yaml file

        Parameters
        ----------
        filename : str
            yaml file name
        libname : str, optional
            library name to be exported
        """
        with open(filename, 'r') as stream:
            ydict = yaml.load(stream)
        logging.debug('Import template')
        for ln, l in ydict.items():
            logging.debug('[Library]' + ln)
            if not ln in self:
                self.add_library(ln)
            self.sel_library(ln)
            for sn, s in l.items():
                logging.debug(' [Template]' + sn)
                pin_dict=dict()
                for pname, p in s['pins'].items():
                    if not 'netname' in p:
                        p['netname']=pname
                    pin_dict[pname]={'netname':p['netname'], 'layer':p['layer'], 'xy':np.array([p['xy0'], p['xy1']])}
                self.add_template(name=sn,libname=libname,xy=np.array([s['xy0'], s['xy1']]),
                                  pins=pin_dict)

    def merge(self, db):
        """
        Merge a GridDB object to self.db

        Parameters
        ----------
        db : TemplateDB
        """
        for ln, l in db.items():
            if not ln in self:
                self.add_library(ln)
            self.sel_library(ln)
            for sn, s in l.items():
                self.add_template(name=sn, libname=ln, xy=s.xy, pins=s.pins)

    # library and template related functions
    def add_library(self, name):
        """
        Add a library to the design dictionary

        Parameters
        ----------
        name : str
            library name
        """
        self[name] = dict()

    def add_template(self, name, libname=None, xy=np.array([[0, 0], [0, 0]]), pins=dict()):
        """
        Add a template to the specified library

        Parameters
        ----------
        name : str
            templatename
        libname : str, optional
            library name (if None, self.plib is used)
        xy : np.array([[float, float], [float, float]]), optional
            template bounding box coordinates
        pins : dict, optional
            pin dictionary
        """
        if libname == None: libname = self._plib
        if not libname in self:
            self.add_library(libname)
        s = TemplateObject(name=name, xy=xy, pins=pins)
        self[libname][name] = s
        logging.debug('AddTemplate: name:' + name + ' xy:' + str(xy.tolist()))
        return s

    def sel_library(self, libname):
        """
        Select a library to work on

        Parameters
        ----------
        libname : str
            library name
        """
        self.plib = libname

    def get_template(self, templatename, libname=None):
        """
        Get a handle of template object

        Parameters
        ----------
        templatename : str
            template name
        libname : str
            library name. If None. laygo.TemplateDB.plib is used

        Returns
        -------
        laygo.TemplateObject.TemplateObject
            template object
        """
        if libname==None: libname=self.plib
        if not templatename in self[libname].keys(): #template is not in the library,
            raise KeyError(templatename+" template is not in "+libname+'. Check corresponding yaml file')
        return self[libname][templatename]
