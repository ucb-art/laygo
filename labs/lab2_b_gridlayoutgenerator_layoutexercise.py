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

"""Lab2: generate layout on abstract grid
   1. Copy this file to working directory
   2. For GDS export, prepare a layermap file
"""
import laygo
import numpy as np
#import logging;logging.basicConfig(level=logging.DEBUG)

laygen = laygo.GridLayoutGenerator(config_file="laygo_config.yaml")
workinglib = 'laygo_working'
utemplib = laygen.tech+'_microtemplates_dense'
metal = laygen.layers['metal']
if laygen.tech=='laygo10n' or laygen.tech=='laygo_faketech': #fake technology
    laygen.use_phantom = True

laygen.add_library(workinglib)
laygen.sel_library(workinglib)

laygen.load_template(filename=laygen.tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
laygen.load_grid(filename=laygen.tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
laygen.sel_template_library(utemplib)
laygen.sel_grid_library(utemplib)
#laygen.templates.display()
laygen.grids.display()

mycell = '_generate_example_3'
pg = 'placement_basic' #placement grid
laygen.add_cell(mycell)
laygen.sel_cell(mycell) #select the cell to work on

#placement on grid
in0=laygen.relplace(name=None, templatename='nmos4_fast_left', gridname=pg)
in1=laygen.relplace(name=None, templatename='nmos4_fast_tap', gridname=pg, refinstname=in0.name)
in2=laygen.relplace(name=None, templatename='nmos4_fast_boundary', gridname=pg, refinstname=in1.name)
in3=laygen.relplace(name=None, templatename='nmos4_fast_center_nf2', gridname=pg, refinstname=in2.name)
in4=laygen.relplace(name=None, templatename='nmos4_fast_center_nf2', gridname=pg, refinstname=in3.name)
in5=laygen.relplace(name=None, templatename='nmos4_fast_center_nf1_right', gridname=pg, refinstname=in4.name)
in6=laygen.relplace(name=None, templatename='nmos4_fast_boundary', gridname=pg, refinstname=in5.name)
in7=laygen.relplace(name=None, templatename='nmos4_fast_right', gridname=pg, refinstname=in6.name)
ip0=laygen.relplace(name=None, templatename='pmos4_fast_left', gridname=pg, refinstname=in0.name, direction='top', transform='MX')
ip1=laygen.relplace(name=None, templatename='pmos4_fast_tap', gridname=pg, refinstname=ip0.name, transform='MX')
ip2=laygen.relplace(name=None, templatename='pmos4_fast_boundary', gridname=pg, refinstname=ip1.name, transform='MX')
ip3=laygen.relplace(name=None, templatename='pmos4_fast_center_nf2', gridname=pg, refinstname=ip2.name, transform='MX')
ip4=laygen.relplace(name=None, templatename='pmos4_fast_center_nf2', gridname=pg, refinstname=ip3.name, transform='MX')
ip5=laygen.relplace(name=None, templatename='pmos4_fast_center_nf1_right', gridname=pg, refinstname=ip4.name, transform='MX')
ip6=laygen.relplace(name=None, templatename='pmos4_fast_boundary', gridname=pg, refinstname=ip5.name, transform='MX')
ip7=laygen.relplace(name=None, templatename='pmos4_fast_right', gridname=pg, refinstname=ip6.name, transform='MX')
'''
#route on grid
laygen.route(name=None, xy0=np.array([15, 3]), xy1=np.array([17, 3]), gridname0='route_M1_M2_mos')
#route on grid with refererence instances
laygen.route(name=None, xy0=np.array([1, 3]), xy1=np.array([3, 3]), gridname0='route_M1_M2_mos',
             refinstname0=ip3.name, refinstname1=ip3.name)
#route on grid with pin references
laygen.route(name=None, xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0='route_M1_M2_mos',
             refinstname0=in3.name, refpinname0='G0', refinstname1=ip3.name, refpinname1='G0')
#via placement on grid
laygen.via(name=None, xy=np.array([15, 3]), gridname='route_M1_M2_mos')
#via placement on grid with reference instance
laygen.via(name=None, xy=np.array([1, 3]), gridname='route_M1_M2_mos', refinstname=ip3.name)
#via placement on grid with pin reference
laygen.via(name=None, xy=np.array([0, 0]), refinstname=in4.name, refpinname='G0', gridname='route_M1_M2_mos')
laygen.via(name=None, xy=np.array([0, 0]), refinstname=ip4.name, refpinname='G0', gridname='route_M1_M2_mos')
#route with automatic via placements (via0, via1)
laygen.route(name=None, xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0='route_M1_M2_mos',
             refinstname0=in3.name, refpinname0='S0', refinstname1=in3.name, refpinname1='S1',
             via0=np.array([[0, 0]]), via1=np.array([[0, 0]]))
laygen.route(name=None, xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0='route_M1_M2_mos',
             refinstname0=ip3.name, refpinname0='S0', refinstname1=ip4.name, refpinname1='S1',
             via0=np.array([[0, 0], [2, 0]]), via1=np.array([[0, 0]]))
'''
#horizontal-vertical route
laygen.route_hv(xy0=[0, 1], xy1=[0, 1], gridname0='route_M2_M3_mos', refinstname0=in3.name, refpinname0='D0',
                refinstname1=ip5.name, refpinname1='D0', via0=[[0, 0]], via1=[[0, 0]])
'''
laygen.route_vh(xy0=[0, 0], xy1=[0, 1], gridname0='route_M2_M3_cmos', refinstname0=in3.name, refpinname0='S0',
                refinstname1=ip4.name, refpinname1='D0', via0=[[0, 0]], via1=[[0, 0]])
'''
#laygen.display()

#bag export, if bag does not exist, gds export
import imp
try:
    imp.find_module('bag')
    import bag
    prj = bag.BagProject()
    laygen.sel_cell(mycell)
    laygen.export_BAG(prj, array_delimiter=['[', ']'])
except ImportError:
    laygen.sel_cell(mycell)  # cell selection
    laygen.export_GDS('output.gds', layermapfile=laygen.tech+".layermap")  # change layermapfile
