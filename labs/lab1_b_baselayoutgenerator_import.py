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

"""Lab1-a: import a layout from BAG or a gds file

Layout information can be imported from BAG or a gds file for post-process. This lab explains the import flow.

Run instructions
----------------
    $ run laygo/labs/lab1_a_baselayoutgenerator_import.py

Notes
-----
    1. laygo_faketech is used for default setting. Update laygo_config.yaml for your technology.
    2. For GDS import, prepare a proper layermap for your technology (usually can be found in techlib directory)
"""

import laygo
import yaml
#import logging;logging.basicConfig(level=logging.DEBUG)

with open("laygo_config.yaml", 'r') as stream:
    techdict = yaml.load(stream)
    tech = techdict['tech_lib']
    metal = techdict['metal_layers']
    via = techdict['via_layers']
    pin = techdict['pin_layers']
    text = techdict['text_layer']
    prbnd = techdict['prboundary_layer']
    res = techdict['physical_resolution']

#working library name
workinglib = 'laygo_working'

#generation instantiation
laygen = laygo.BaseLayoutGenerator(res=0.0025) #res should be your minimum grid resolution
#library generation
laygen.add_library(workinglib)
laygen.sel_library(workinglib)

#bag import, if bag does not exist, gds import
import imp
try:
    imp.find_module('bag')
    #bag import
    print("import from BAG")
    import bag
    prj = bag.BagProject()
    laygen.import_BAG(prj, workinglib).display()
    laygen.display()
except ImportError:
    #gds import
    print("import from GDS")
    laygen.import_GDS('lab1_generated.gds', layermapfile=tech+".layermap")  # change layermapfile
    laygen.import_GDS('lab1_generated2.gds', layermapfile=tech+".layermap")
    laygen.display()
