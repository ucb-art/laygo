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

"""Lab1-a: generate a layout on physical grid

The layout generation flow can be scripted with physical grid information. It will lack of process interoperabilty but
is useful for some cases; i.e. top integrations or routing to IPs not generated from BAG or laygo. This lab shows how
a MOM cap construction flow can be scripted.

Run instructions
----------------
    $ run laygo/labs/lab1_a_baselayoutgenerator_export.py

Notes
-----
    1. laygo_faketech is used for default setting. Update laygo_config.yaml for your technology.
    2. For GDS export, prepare a proper layermap for your technology (usually can be found in techlib directory)
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

import laygo
import numpy as np
import yaml
#import logging; logging.basicConfig(level=logging.DEBUG)

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

laygen = laygo.BaseLayoutGenerator(res=res) #res should be your minimum grid resolution
#library addition (you should create the workinglib library in BAG or virtuoso before running this script
#                  if you are exporting to BAG)
laygen.add_library(workinglib)
laygen.sel_library(workinglib)

#example layout generation (momcap)
#parameters
w=0.05 #width
p=0.1  #pitch
f=10   #finger
l=p*(f+1)  #length
#cell creation
mycell = '_generate_example_1'
laygen.add_cell(mycell)
laygen.sel_cell(mycell)

#mom_metal
mom_coord_ref=np.arange(p, p*(f+1), p)
mom_coord=np.array([[mom_coord_ref-w/2, np.zeros(f)],[mom_coord_ref+w/2, np.ones(f)*l]])
mom_coord_1=np.transpose(mom_coord, axes=[2, 0, 1])
mom_coord_2=np.transpose(np.fliplr(mom_coord), axes=[2, 0, 1])
laygen.add_rect(None, mom_coord_1, metal[1])
laygen.add_rect(None, mom_coord_2, metal[2])
laygen.add_pin(None, 'A', mom_coord_1[0], pin[1])
laygen.add_pin(None, 'B', mom_coord_1[-1], pin[1])

#mom_via
via_a_coord_ref=np.arange(p, p*(f+1), p*2)
via_a_coord_ref=np.meshgrid(via_a_coord_ref, via_a_coord_ref)
via_a_coord_ref=[via_a_coord_ref[0].flatten(), via_a_coord_ref[1].flatten()]
via_a_coord=np.array([[via_a_coord_ref[0]-w/2, via_a_coord_ref[1]-w/2],[via_a_coord_ref[0]+w/2, via_a_coord_ref[1]+w/2]])
via_a_coord=np.transpose(via_a_coord, axes=[2, 0, 1])
laygen.add_rect(None, via_a_coord, via[1])

via_b_coord_ref=np.arange(p*2, p*(f+1), p*2)
via_b_coord_ref=np.meshgrid(via_b_coord_ref, via_b_coord_ref)
via_b_coord_ref=[via_b_coord_ref[0].flatten(), via_b_coord_ref[1].flatten()]
via_b_coord=np.array([[via_b_coord_ref[0]-w/2, via_b_coord_ref[1]-w/2],[via_b_coord_ref[0]+w/2, via_b_coord_ref[1]+w/2]])
via_b_coord=np.transpose(via_b_coord, axes=[2, 0, 1])
laygen.add_rect(None, via_b_coord, via[1])

mycell2 = '_generate_example_2'
laygen.add_cell(mycell2)
laygen.sel_cell(mycell2)
laygen.add_inst(None, workinglib, mycell, xy=np.array([2, 0]))
laygen.add_inst(None, workinglib, mycell, xy=np.array([0, 2]), shape=np.array([2, 3]),
                spacing=np.array([1, 2]), transform='MX')
laygen.add_text(None, 'text0', np.array([1, 1]), text)
laygen.display()

#bag export, if bag does not exist, gds export
from imp import find_module
try:
    find_module('bag')
    #bag export
    print("export to BAG")
    import bag
    prj = bag.BagProject()
    laygen.sel_cell(mycell)
    laygen.export_BAG(prj)
    laygen.sel_cell(mycell2)
    laygen.export_BAG(prj)
except ImportError:
    #gds export
    print("export to GDS")
    laygen.sel_cell(mycell) #cell selection
    laygen.export_GDS('lab1_generated.gds', layermapfile=tech+".layermap")
    laygen.sel_cell(mycell2)
    laygen.export_GDS('lab1_generated2.gds', cellname=[mycell, mycell2], layermapfile=tech+".layermap")