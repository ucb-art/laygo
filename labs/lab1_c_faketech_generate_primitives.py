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


"""Lab1-a: generate primitive template layouts for fake technology (laygo_faketech)
    For real technologies, primitive layouts are usually constructed manually.

Run instructions
----------------
    $ run laygo/labs/lab1_c_faketechexercise.py

Notes
-----
    1. This script will generate laygo_faketech_microtemplates_dense.gds, which will be used for lab2_a
"""

__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

import laygo
import numpy as np
import yaml
from copy import deepcopy
#import logging;logging.basicConfig(level=logging.DEBUG)

def construct_mosfet_structure(laygen, cpo = 0.2, prgrid = [0.2, 0.05], nf=2, h=16,
                               wds_m1 = 0.1, hds_m1 = 0.3, ofysd_m1 = 0.3,
                               wg_m1 = 0.15, hg_m1 = 0.15, ofxg_m1 = 0.2, ofyg_m1 = 0.6,
                               generate_sd_pins = True, generate_gate_pins = True,
                               sd_pinname_list = ['S0', 'D0', 'S1'], gate_pinname_list = ['G0'],
                               sd_netname_list = None, gate_netname_list = None
                               ):
    # netname handling
    if sd_netname_list==None:
        sd_netname_list=sd_pinname_list
    if gate_netname_list==None:
        gate_netname_list=gate_pinname_list
    # prboundary
    laygen.add_rect(None, [[0, 0], [prgrid[0] * nf, prgrid[1] * h]], prbnd)
    # source/drain pins
    if generate_sd_pins:
        for i, n in enumerate(sd_pinname_list):
            if not n==None:
                xy_sd = np.array([[-wds_m1 / 2, ofysd_m1 - hds_m1 / 2], [wds_m1 / 2, ofysd_m1 + hds_m1 / 2]]) \
                       + np.array([i * cpo, 0])
                laygen.add_rect(None, xy_sd, metal[1])
                laygen.add_pin(n, sd_netname_list[i], xy_sd, pin[1])
                if not n == sd_netname_list[i]:
                    laygen.add_pin(sd_netname_list[i], sd_netname_list[i], xy_sd, text)
    # gate pins
    if generate_gate_pins:
        for i, n in enumerate(gate_pinname_list):
            xy_g = np.array([[ofxg_m1 - wg_m1 / 2, ofyg_m1 - hg_m1 / 2], [ofxg_m1 + wg_m1 / 2, ofyg_m1 + hg_m1 / 2]]) \
                   + np.array([i*2*cpo, 0])
            laygen.add_rect(None, xy_g, metal[1])
            laygen.add_pin(n, gate_netname_list[i], xy_g, pin[1])
            if not n == gate_netname_list[i]:
                laygen.add_pin(gate_netname_list[i], gate_netname_list[i], xy_g, text)



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
workinglib = tech+'_microtemplates_dense'
laygen = laygo.BaseLayoutGenerator(res=res) #res should be your minimum grid resolution
#library creation (you should create your library in BAG or virtuoso if you'd like to export to BAG
laygen.add_library(workinglib)
laygen.sel_library(workinglib)

#via parameters
params_via = {
    'via_M1_M2_0': {
        'layer_vert': ['M1', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'layer_via' : ['VIA1', 'drawing'],
        'xwidth': 0.1,
        'ywidth': 0.1,
        'xextend': 0.1,
        'yextend': 0.1,
    },
    'via_M1_M2_1': {
        'layer_vert': ['M1', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'layer_via' : ['VIA1', 'drawing'],
        'xwidth': 0.1,
        'ywidth': 0.2,
        'xextend': 0.1,
        'yextend': 0.1,
    },
    'via_M2_M3_0': {
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'layer_via': ['VIA2', 'drawing'],
        'xwidth': 0.1,
        'ywidth': 0.1,
        'xextend': 0.1,
        'yextend': 0.1,
    },
    'via_M2_M3_1': {
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'layer_via': ['VIA2', 'drawing'],
        'xwidth': 0.1,
        'ywidth': 0.2,
        'xextend': 0.1,
        'yextend': 0.1,
    },
    'via_M3_M4_0': {
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M4', 'drawing'],
        'layer_via': ['VIA3', 'drawing'],
        'xwidth': 0.1,
        'ywidth': 0.1,
        'xextend': 0.1,
        'yextend': 0.1,
    },
    'via_M3_M4_1': {
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M4', 'drawing'],
        'layer_via': ['VIA3', 'drawing'],
        'xwidth': 0.1,
        'ywidth': 0.2,
        'xextend': 0.1,
        'yextend': 0.1,
    },
}

#grid parameters
params_placement_grid = {
    'placement_basic': {
        'xy': [0.2, 0.05]
    }
}
params_route_grid = {
    'route_M1_M2_basic': {
        'viamap': {
            'via_M1_M2_0':[[0, 0]]
        },
        'layer_vert': ['M1', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0':    [0.0, 0.0],
        'xy1':    [0.2, 0.2],
        'xgrid':  [0.0],
        'ygrid':  [0.0],
        'xwidth': [0.1],
        'ywidth': [0.1],
    },
    'route_M1_M2_basic_thick': {
        'viamap': {
            'via_M1_M2_1':[[0, 0]]
        },
        'layer_vert': ['M1', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0':    [0.0, 0.0],
        'xy1':    [0.2, 0.4],
        'xgrid':  [0.0],
        'ygrid':  [0.0],
        'xwidth': [0.1],
        'ywidth': [0.2],
    },
    'route_M1_M2_mos': {
        'viamap': {
            'via_M1_M2_0':[[0, 1], [0, 2], [0, 3]],
            'via_M1_M2_1':[[0, 0]]
        },
        'layer_vert': ['M1', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0':    [0.0, 0.0],
        'xy1':    [0.2, 0.9],
        'xgrid':  [0.0],
        'ygrid':  [0.0, 0.25, 0.45, 0.7],
        'xwidth': [0.1],
        'ywidth': [0.2, 0.1, 0.1, 0.1],
    },
    'route_M1_M2_cmos': {
        'viamap': {
            'via_M1_M2_0':[[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7]],
            'via_M1_M2_1':[[0, 0], [0, 8]]
        },
        'layer_vert': ['M1', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0':    [0.0, 0.0],
        'xy1':    [0.2, 1.8],
        'xgrid':  [0.0],
        'ygrid':  [0.0, 0.25, 0.45, 0.7, 0.9, 1.1, 1.35, 1.55, 1.8],
        'xwidth': [0.1],
        'ywidth': [0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2],
    },
    'route_M2_M3_basic': {
        'viamap': {
            'via_M2_M3_0': [[0, 0]]
        },
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.2, 0.2],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.1],
        'ywidth': [0.1],
    },
    'route_M2_M3_basic_thick': {
        'viamap': {
            'via_M2_M3_1': [[0, 0]]
        },
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.2, 0.4],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.1],
        'ywidth': [0.2],
    },
    'route_M2_M3_cmos': {
        'viamap': {
            'via_M2_M3_0': [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7]],
            'via_M2_M3_1': [[0, 0], [0, 8]]
        },
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.2, 1.8],
        'xgrid': [0.0],
        'ygrid': [0.0, 0.25, 0.45, 0.7, 0.9, 1.1, 1.35, 1.55, 1.8],
        'xwidth': [0.1],
        'ywidth': [0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2],
    },
    'route_M2_M3_mos': {
        'viamap': {
            'via_M2_M3_0': [[0, 1], [0, 2], [0, 3]],
            'via_M2_M3_1': [[0, 0]]
        },
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.2, 0.9],
        'xgrid': [0.0],
        'ygrid': [0.0, 0.25, 0.45, 0.7],
        'xwidth': [0.1],
        'ywidth': [0.2, 0.1, 0.1, 0.1],
    },
    'route_M3_M4_basic': {
        'viamap': {
            'via_M3_M4_0': [[0, 0]]
        },
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M4', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.2, 0.2],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.1],
        'ywidth': [0.1],
    },
}

#transistor parameters
params_transistor_default = {
    'cpo':0.2, #contact poly pitch
    'prgrid':params_placement_grid['placement_basic']['xy'], #placement grids
    'nf':2, #number of fingers
    'h':18, #cell height
    'wds_m1':0.1, #drain/source pin width
    'hds_m1':0.3, #drain/source pin height
    'ofysd_m1':0.35, #source/drain pin y-center
    'wg_m1':0.15, #gate pin width
    'hg_m1':0.15, #gate pin height
    'ofxg_m1':0.2, #gate pin x-center
    'ofyg_m1':0.7, #gate pin y-center
    'generate_sd_pins':True,
    'generate_gate_pins':True,
    'sd_pinname_list':['S0', 'D0', 'S1'],
    'gate_pinname_list':['G0'],
}

mycells=[]

#via generation
for prgn, prg in params_via.items():
    mycells.append(prgn)
    laygen.add_cell(prgn)
    laygen.sel_cell(prgn)
    # via
    laygen.add_rect(None, [[-prg['xwidth']/2, -prg['ywidth']/2], [prg['xwidth']/2, prg['ywidth']/2]], prg['layer_via'])
    # vertical metal
    laygen.add_rect(None, [[-prg['xwidth'] / 2, -prg['yextend'] - prg['ywidth'] / 2],
                           [prg['xwidth'] / 2, prg['yextend'] + prg['ywidth'] / 2]],
                            prg['layer_vert'])
    # horizontal metal
    laygen.add_rect(None, [[-prg['xextend'] - prg['xwidth'] / 2, -prg['ywidth'] / 2],
                           [prg['xextend'] + prg['xwidth'] / 2, prg['ywidth'] / 2]],
                            prg['layer_hori'])

#grid
for ppgn, ppg in params_placement_grid.items():
    mycells.append(ppgn)
    laygen.add_cell(ppgn)
    laygen.sel_cell(ppgn)
    # prboundary
    laygen.add_rect(None, [[0, 0], ppg['xy']], prbnd)

for prgn, prg in params_route_grid.items():
    mycells.append(prgn)
    laygen.add_cell(prgn)
    laygen.sel_cell(prgn)
    # prboundary
    laygen.add_rect(None, [prg['xy0'], prg['xy1']], prbnd)
    # xgrid
    for i, xg in enumerate(prg['xgrid']):
        laygen.add_rect(None, [[xg - prg['xwidth'][i] / 2, prg['xy0'][1]],
                               [xg + prg['xwidth'][i] / 2, prg['xy1'][1] + prg['xwidth'][i]]],
                        prg['layer_vert'])
    # ygrid
    for i, yg in enumerate(prg['ygrid']):
        laygen.add_rect(None, [[prg['xy0'][0], yg - prg['ywidth'][i] / 2],
                               [prg['xy1'][0] + prg['ywidth'][i], yg + prg['ywidth'][i] / 2]],
                        prg['layer_hori'])
    # viamap
    for vname, vxy in prg['viamap'].items():
        for _vxy in vxy:
            laygen.add_inst(None, workinglib, vname, xy=[prg['xgrid'][_vxy[0]], prg['ygrid'][_vxy[1]]])

#transistor family
header_list = ['nmos4_fast', 'pmos4_fast']
for header in header_list:
    mycell = header+'_boundary' #boundary cell placed at edges of a transistor row
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 1 #number of fingers
    params['generate_sd_pins'] = False
    params['generate_gate_pins'] = False
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_center_2stack' #2-stack mos (mostly for cascode)
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 2 #number of fingers
    params['sd_pinname_list'] = ['S0', None, 'D0']
    params['ofxg_m1'] = 0.0
    params['gate_pinname_list'] = ['G0', 'G1']
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_center_nf1_left' #1-finger mos with a gate pin at left side
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['ofxg_m1'] = 0 #gate pin x-center
    params['nf'] = 1 #number of fingers
    params['sd_pinname_list'] = ['S0', 'D0']
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_center_nf1_right' #1-finger mos with a gate pin at right side
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['ofxg_m1'] = params['cpo'] #gate pin x-center
    params['nf'] = 1 #number of fingers
    params['sd_pinname_list'] = ['S0', 'D0']
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_center_nf2' #2-finger mos
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 2 #number of fingers
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_dmy_nf2' #2-finger dummy mos
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 2 #number of fingers
    params['generate_gate_pins'] = False
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_space' #space
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 1 #number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_1x'  # space
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 1  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_2x'  # space_2x
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 2  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_4x'  # space_4x
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 4  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_nf2'  # space_nf2
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 2  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_nf4'  # space_nf4
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 4  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_left' #left side
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 6 #number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_right' #right side
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 6 #number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_tap' #tap
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 7 #number of fingers
    params['generate_gate_pins'] = False
    params['sd_pinname_list'] = [None, None, None, 'TAP0', 'TAP1', None, None, None]
    params['sd_netname_list'] = [None, None, None, 'VSS', 'VSS', None, None, None]
    construct_mosfet_structure(laygen, **params)

#bag export, if bag does not exist, gds export
from imp import find_module
try:
    find_module('bag')
    #bag export
    print("export to BAG")
    import bag
    prj = bag.BagProject()
    laygen.sel_cell(mycell)
    laygen.export_BAG(prj, array_delimiter=['[', ']'])
except ImportError:
    #gds export
    print("export to GDS")
    #laygen.sel_cell(mycell) #cell selection
    laygen.export_GDS(workinglib+'.gds', cellname=mycells, layermapfile=tech+".layermap")

