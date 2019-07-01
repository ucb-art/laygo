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


"""Lab1-a: generate primitive template layouts for fake technology (laygo_cds_ff)
    For real technologies, primitive layouts are usually constructed manually.

Run instructions
----------------
    $ run laygo/labs/lab1_c_cds_ff_mpt_generate_primitives.py

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
                               sd_netname_list = None, gate_netname_list = None,
                               instance_cellname_list = None, instance_xy_list = None,
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
                laygen.add_pin(n, sd_netname_list[i], xy_sd, pin[1])
                if n != sd_netname_list[i]:
                    laygen.add_pin(n+'_net', n, xy_sd, text)
    # gate pins
    if generate_gate_pins:
        for i, n in enumerate(gate_pinname_list):
            xy_g = np.array([[ofxg_m1 - wg_m1 / 2, ofyg_m1 - hg_m1 / 2], [ofxg_m1 + wg_m1 / 2, ofyg_m1 + hg_m1 / 2]]) \
                   + np.array([i*2*cpo, 0])
            #laygen.add_rect(None, xy_g, pin[1])
            laygen.add_pin(n, gate_netname_list[i], xy_g, pin[1])
            if not n == gate_netname_list[i]:
                laygen.add_pin(n+'_net', n, xy_g, text)
    # instances
    if instance_cellname_list:
        for inst, xy in zip(instance_cellname_list, instance_xy_list):
            laygen.add_inst(None, workinglib, inst, xy=xy)

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
        'layer_vert': metal[1],
        'layer_hori': metal[2],
        'layer_via' : via[1],
        'xwidth': 0.032,
        'ywidth': 0.032,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.00,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
    'via_M1_M2_1': {
        'layer_vert': metal[1],
        'layer_hori': metal[2],
        'layer_via' : via[1],
        'xwidth': 0.032,
        'ywidth': 0.064,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.016,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
    'via_M1_M2_2': {
        'layer_vert': metal[1],
        'layer_hori': metal[2],
        'layer_via' : via[1],
        'xwidth': 0.032,
        'ywidth': 0.032,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.00,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.024,
    },
    'via_M2_M3_0': {
        'layer_vert': metal[3],
        'layer_hori': metal[2],
        'layer_via' : via[2],
        'xwidth': 0.032,
        'ywidth': 0.032,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.00,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
    'via_M2_M3_1': {
        'layer_vert': metal[3],
        'layer_hori': metal[2],
        'layer_via' : via[2],
        'xwidth': 0.032,
        'ywidth': 0.064,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.016,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
    'via_M3_M4_0': {
        'layer_vert': metal[3],
        'layer_hori': metal[4],
        'layer_via' : via[3],
        'xwidth': 0.032,
        'ywidth': 0.032,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.00,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
    'via_M3_M4_1': {
        'layer_vert': metal[3],
        'layer_hori': metal[4],
        'layer_via' : via[3],
        'xwidth': 0.032,
        'ywidth': 0.032,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.016,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
    'via_M4_M5_0': {
        'layer_vert': metal[5],
        'layer_hori': metal[4],
        'layer_via' : via[4],
        'xwidth': 0.032,
        'ywidth': 0.032,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.00,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
    'via_M4_M5_1': {
        'layer_vert': metal[5],
        'layer_hori': metal[4],
        'layer_via' : via[4],
        'xwidth': 0.032,
        'ywidth': 0.032,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.016,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
    'via_M5_M6_0': {
        'layer_vert': metal[5],
        'layer_hori': metal[6],
        'layer_via' : via[5],
        'xwidth': 0.032,
        'ywidth': 0.032,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.00,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
    'via_M5_M6_1': {
        'layer_vert': metal[5],
        'layer_hori': metal[6],
        'layer_via' : via[5],
        'xwidth': 0.032,
        'ywidth': 0.032,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.016,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
    'via_M6_M7_0': {
        'layer_vert': metal[7],
        'layer_hori': metal[6],
        'layer_via' : via[6],
        'xwidth': 0.032,
        'ywidth': 0.032,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.00,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
    'via_M6_M7_1': {
        'layer_vert': metal[7],
        'layer_hori': metal[6],
        'layer_via' : via[6],
        'xwidth': 0.032,
        'ywidth': 0.032,
        'extend_x_hori': 0.04,
        'extend_y_hori': 0.016,
        'extend_x_vert': 0.00,
        'extend_y_vert': 0.04,
    },
}

#grid parameters
params_placement_grid = {
    'placement_basic': {
        'xy': [0.086, 0.048]
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
        'xy1':    [0.086, 0.096],
        'xgrid':  [0.0],
        'ygrid':  [0.0],
        'xwidth': [0.032],
        'ywidth': [0.032],
    },
    'route_M1_M2_basic_thick': {
        'viamap': {
            'via_M1_M2_1':[[0, 0]]
        },
        'layer_vert': ['M1', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0':    [0.0, 0.0],
        'xy1':    [0.086, 0.192],
        'xgrid':  [0.0],
        'ygrid':  [0.0],
        'xwidth': [0.032],
        'ywidth': [0.096],
    },
    'route_M1_M2_mos': {
        'viamap': {
            'via_M1_M2_0':[[0, 1], [0, 2]],
            'via_M1_M2_1':[[0, 0]],
            'via_M1_M2_2':[[0, 3]]
        },
        'layer_vert': ['M1', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0':    [0.0, 0.0],
        'xy1':    [0.086, 0.48],
        'xgrid':  [0.0],
        'ygrid':  [0.0, 0.144, 0.24, 0.384],
        'xwidth': [0.032],
        'ywidth': [0.096, 0.032, 0.032, 0.032],
    },
    'route_M1_M2_cmos': {
        'viamap': {
            'via_M1_M2_0':[[0, 1], [0, 2], [0, 4], [0, 6], [0, 7]],
            'via_M1_M2_1':[[0, 0], [0, 8]],
            'via_M1_M2_2':[[0, 3], [0, 5]]
        },
        'layer_vert': ['M1', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0':    [0.0, 0.0],
        'xy1':    [0.086, 0.96],
        'xgrid':  [0.0],
        'ygrid':  [0.0, 0.144, 0.24, 0.384, 0.48, 0.576, 0.72, 0.816, 0.96],
        'xwidth': [0.032],
        'ywidth': [0.096, 0.032, 0.032, 0.032, 0.032, 0.032, 0.032, 0.032, 0.096],
    },
    'route_M2_M3_basic': {
        'viamap': {
            'via_M2_M3_0': [[0, 0]]
        },
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.086, 0.032],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.032],
        'ywidth': [0.032],
    },
    'route_M2_M3_thick_basic': {
        'viamap': {
            'via_M2_M3_1': [[0, 0]]
        },
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.086, 0.192],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.032],
        'ywidth': [0.096],
    },
    'route_M2_M3_mos': {
        'viamap': {
            'via_M2_M3_0': [[0, 1], [0, 2], [0, 3]],
            'via_M2_M3_1': [[0, 0]]
        },
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.086, 0.48],
        'xgrid': [0.0],
        'ygrid': [0.0, 0.144, 0.24, 0.384],
        'xwidth': [0.032],
        'ywidth': [0.096, 0.032, 0.032, 0.032],
    },
    'route_M2_M3_cmos': {
        'viamap': {
            'via_M2_M3_0': [[0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7]],
            'via_M2_M3_1': [[0, 0], [0, 8]]
        },
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M2', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.086, 0.96],
        'xgrid': [0.0],
        'ygrid': [0.0, 0.144, 0.24, 0.384, 0.48, 0.576, 0.72, 0.816, 0.96],
        'xwidth': [0.032],
        'ywidth': [0.096, 0.032, 0.032, 0.032, 0.032, 0.032, 0.032, 0.032, 0.096],
    },
    'route_M3_M4_basic': {
        'viamap': {
            'via_M3_M4_0': [[0, 0]]
        },
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M4', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.086, 0.064],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.032],
        'ywidth': [0.032],
    },
    'route_M3_M4_thick': {
        'viamap': {
            'via_M3_M4_1': [[0, 0]]
        },
        'layer_vert': ['M3', 'drawing'],
        'layer_hori': ['M4', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.192, 0.192],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.096],
        'ywidth': [0.096],
    },
    'route_M4_M5_basic': {
        'viamap': {
            'via_M4_M5_0': [[0, 0]]
        },
        'layer_vert': ['M5', 'drawing'],
        'layer_hori': ['M4', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.086, 0.064],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.032],
        'ywidth': [0.032],
    },
    'route_M4_M5_thick': {
        'viamap': {
            'via_M4_M5_1': [[0, 0]]
        },
        'layer_vert': ['M5', 'drawing'],
        'layer_hori': ['M4', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.192, 0.192],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.096],
        'ywidth': [0.096],
    },
    'route_M5_M6_basic': {
        'viamap': {
            'via_M5_M6_0': [[0, 0]]
        },
        'layer_vert': ['M5', 'drawing'],
        'layer_hori': ['M6', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.086, 0.064],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.032],
        'ywidth': [0.032],
    },
    'route_M5_M6_thick': {
        'viamap': {
            'via_M5_M6_1': [[0, 0]]
        },
        'layer_vert': ['M5', 'drawing'],
        'layer_hori': ['M6', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.192, 0.192],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.096],
        'ywidth': [0.096],
    },
    'route_M5_M6_basic_thick': {
        'viamap': {
            'via_M5_M6_1':[[0, 0]]
        },
        'layer_vert': ['M5', 'drawing'],
        'layer_hori': ['M6', 'drawing'],
        'xy0':    [0.0, 0.0],
        'xy1':    [0.086, 0.192],
        'xgrid':  [0.0],
        'ygrid':  [0.0],
        'xwidth': [0.032],
        'ywidth': [0.096],
    },
    'route_M6_M7_basic': {
        'viamap': {
            'via_M6_M7_0': [[0, 0]]
        },
        'layer_vert': ['M7', 'drawing'],
        'layer_hori': ['M6', 'drawing'],
        'xy0': [0.0, 0.0],
        'xy1': [0.086, 0.064],
        'xgrid': [0.0],
        'ygrid': [0.0],
        'xwidth': [0.032],
        'ywidth': [0.032],
    },
}

#transistor parameters
params_transistor_default = {
    'cpo':0.086, #contact poly pitch
    'prgrid':params_placement_grid['placement_basic']['xy'], #placement grids
    'nf':2, #number of fingers
    'h':10, #cell height
    'wds_m1':0.032, #drain/source pin width
    'hds_m1':0.178, #drain/source pin height
    'ofysd_m1':0.192, #source/drain pin y-center
    'wg_m1':0.08, #gate pin width
    'hg_m1':0.08, #gate pin height
    'ofxg_m1':0.086, #gate pin x-center
    'ofyg_m1':0.384, #gate pin y-center
    'generate_sd_pins':True,
    'generate_gate_pins':True,
    'sd_pinname_list':['S0', 'D0', 'S1'],
    'gate_pinname_list':['G0'],
    'instance_cellname_list':None,       #instance addition
    'instance_xy_list':None,
}

mycells=[]

#via generation
for prgn, prg in params_via.items():
    mycells.append(prgn)
    laygen.add_cell(prgn)
    laygen.sel_cell(prgn)
    if not 'extend_x_vert' in prg: prg['extend_x_vert']=0
    if not 'extend_y_hori' in prg: prg['extend_y_hori']=0
    # via
    laygen.add_rect(None, [[-prg['xwidth']/2, -prg['ywidth']/2], [prg['xwidth']/2, prg['ywidth']/2]], prg['layer_via'])
    # vertical metal
    laygen.add_rect(None, [[-prg['extend_x_vert'] - prg['xwidth'] / 2, -prg['extend_y_vert'] - prg['ywidth'] / 2],
                           [prg['extend_x_vert'] + prg['xwidth'] / 2, prg['extend_y_vert'] + prg['ywidth'] / 2]],
                            prg['layer_vert'])
    # horizontal metal 
    laygen.add_rect(None, [[-prg['extend_x_hori'] - prg['xwidth'] / 2, -prg['extend_y_hori']- prg['ywidth'] / 2],
                           [prg['extend_x_hori'] + prg['xwidth'] / 2, prg['extend_y_hori'] + prg['ywidth'] / 2]],
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
    params['instance_cellname_list'] = ['_'+header+'_boundary_base']
    params['instance_xy_list'] = [[0, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_center_2stack' #2-stack mos (mostly for cascode)
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 2 #number of fingers
    params['ofxg_m1'] = 0 #gate pin x-center
    params['gate_pinname_list'] = ['G0', 'G1']
    params['sd_pinname_list'] = ['S0', None, 'D0']
    params['instance_cellname_list'] = ['_'+header+'_base_nf1', '_'+header+'_base_nf1'] \
                                       + ['_gate_base_nf1_left', '_gate_base_nf1_right'] \
                                       + ['_sd_base', '_sd_base'] 
    params['instance_xy_list'] = [[0, 0], [params['cpo'], 0]] \
                                 + [[0, 0], [params['cpo'], 0]] \
                                 + [[0, 0], [params['cpo']*2, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_center_nf1_left' #1-finger mos with a gate pin at left side
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['ofxg_m1'] = 0 #gate pin x-center
    params['nf'] = 1 #number of fingers
    params['sd_pinname_list'] = ['S0', 'D0']
    params['instance_cellname_list'] = ['_'+header+'_base_nf1'] \
                                       + ['_gate_base_nf1_left'] \
                                       + ['_sd_base', '_sd_base'] 
    params['instance_xy_list'] = [[0, 0]] \
                                 + [[0, 0]] \
                                 + [[0, 0], [params['cpo'], 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_center_nf1_right' #1-finger mos with a gate pin at right side
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['ofxg_m1'] = params['cpo'] #gate pin x-center
    params['nf'] = 1 #number of fingers
    params['sd_pinname_list'] = ['S0', 'D0']
    params['instance_cellname_list'] = ['_'+header+'_base_nf1'] \
                                       + ['_gate_base_nf1_right'] \
                                       + ['_sd_base', '_sd_base'] 
    params['instance_xy_list'] = [[0, 0]] \
                                 + [[0, 0]] \
                                 + [[0, 0], [params['cpo'], 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_center_nf2' #2-finger mos
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 2 #number of fingers
    params['instance_cellname_list'] = ['_'+header+'_base_nf1', '_'+header+'_base_nf1'] \
                                       + ['_gate_base_nf2'] \
                                       + ['_sd_base', '_sd_base', '_sd_base'] 
    params['instance_xy_list'] = [[0, 0], [params['cpo'], 0]] \
                                 + [[0, 0]] \
                                 + [[0, 0], [params['cpo'], 0], [params['cpo']*2, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_dmy_nf2' #2-finger dummy mos
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 2 #number of fingers
    params['generate_gate_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_base_nf1', '_'+header+'_base_nf1'] \
                                       + ['_gate_dmy_base_nf2'] \
                                       + ['_sd_base', '_sd_base', '_sd_base'] 
    params['instance_xy_list'] = [[0, 0], [params['cpo'], 0]] \
                                 + [[0, 0]] \
                                 + [[0, 0], [params['cpo'], 0], [params['cpo']*2, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_space' #space
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 1 #number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_space_base_nf1'] 
    params['instance_xy_list'] = [[0, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_1x'  # space
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 1  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_space_base_nf1'] 
    params['instance_xy_list'] = [[0, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_2x'  # space_2x
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 2  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_space_base_nf1']*2 
    params['instance_xy_list'] = [[0, 0], [params['cpo'], 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_4x'  # space_4x
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 4  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_space_base_nf1']*4 
    params['instance_xy_list'] = [[0, 0], [params['cpo'], 0], [2*params['cpo'], 0], [3*params['cpo'], 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_nf2'  # space_nf2
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 2  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_space_base_nf1']*2 
    params['instance_xy_list'] = [[0, 0], [params['cpo'], 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_nf4'  # space_nf4
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 4  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_space_base_nf1']*4 
    params['instance_xy_list'] = [[0, 0], [params['cpo'], 0], [2*params['cpo'], 0], [3*params['cpo'], 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_left' #left side
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 6 #number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_space_base_nf1']*2 
    params['instance_xy_list'] = [[params['cpo']*4, 0], [params['cpo']*5, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_right' #right side
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 6 #number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_space_base_nf1']*2 
    params['instance_xy_list'] = [[params['cpo']*0, 0], [params['cpo']*1, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_tap' #tap
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 7 #number of fingers
    params['generate_gate_pins'] = False
    params['sd_pinname_list'] = [None, None, None, 'TAP0', 'TAP1', None, None, None]
    if header.startswith('nmos'):
        params['sd_netname_list'] = [None, None, None, 'VSS', 'VSS', None, None, None]
    else:
        params['sd_netname_list'] = [None, None, None, 'VDD', 'VDD', None, None, None]
    params['instance_cellname_list'] = ['_'+header+'_space_base_nf1']*2 \
                                       + ['_'+header+'_space_base_nf1']*2 \
                                       + ['_sd_base', '_sd_base'] \
                                       + ['_'+header+'_base_tap_base']
    params['instance_xy_list'] = [[params['cpo']*i, 0] for i in range(2)] \
                                 +[[params['cpo']*i, 0] for i in range(5, 7)] \
                                 + [[params['cpo']*3, 0], [params['cpo']*4, 0]] \
                                 + [[0, 0]]
    construct_mosfet_structure(laygen, **params)

#tap family
header_list = ['ptap_fast', 'ntap_fast']
for header in header_list:
    mycell = header+'_boundary' #boundary cell placed at edges of a transistor row
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 1 #number of fingers
    params['generate_sd_pins'] = False
    params['generate_gate_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_boundary_base']
    params['instance_xy_list'] = [[0, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_center_nf2' #2-finger mos
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 2 #number of fingers
    params['generate_gate_pins'] = False
    params['sd_pinname_list'] = ['TAP0', 'TAP1', 'TAP2']
    if header.startswith('ptap'):
        params['sd_netname_list'] = ['VSS', 'VSS', 'VSS']
    else:
        params['sd_netname_list'] = ['VDD', 'VDD', 'VDD']
    params['instance_cellname_list'] = ['_'+header+'_base_nf1', '_'+header+'_base_nf1'] \
                                       + ['_sd_base', '_sd_base', '_sd_base'] 
    params['instance_xy_list'] = [[0, 0], [params['cpo'], 0]] \
                                 + [[0, 0], [params['cpo'], 0], [params['cpo']*2, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_center_nf1' #1-finger mos with a gate pin at left side
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['ofxg_m1'] = 0 #gate pin x-center
    params['nf'] = 1 #number of fingers
    params['generate_gate_pins'] = False
    params['sd_pinname_list'] = ['TAP0', 'TAP1']
    if header.startswith('ptap'):
        params['sd_netname_list'] = ['VSS', 'VSS']
    else:
        params['sd_netname_list'] = ['VDD', 'VDD']
    params['instance_cellname_list'] = ['_'+header+'_base'] \
                                       + ['_sd_base', '_sd_base'] 
    params['instance_xy_list'] = [[0, 0]] \
                                 + [[0, 0], [params['cpo'], 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space'  # space
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 1  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_base_nf1']
    params['instance_xy_list'] = [[0, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_nf2'  # space_nf2
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 2  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_base_nf1']*2 
    params['instance_xy_list'] = [[0, 0], [params['cpo'], 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header + '_space_nf4'  # space_nf4
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params = deepcopy(params_transistor_default)
    params['nf'] = 4  # number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_base_nf1']*4 
    params['instance_xy_list'] = [[0, 0], [params['cpo'], 0], [2*params['cpo'], 0], [3*params['cpo'], 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_left' #left side
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 6 #number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_base_nf1']*2 
    params['instance_xy_list'] = [[params['cpo']*4, 0], [params['cpo']*5, 0]]
    construct_mosfet_structure(laygen, **params)

    mycell = header+'_right' #right side
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = 6 #number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    params['instance_cellname_list'] = ['_'+header+'_base_nf1']*2 
    params['instance_xy_list'] = [[params['cpo']*0, 0], [params['cpo']*1, 0]]
    construct_mosfet_structure(laygen, **params)



#boundary cell generation
bnd_suffix = ['_topleft', '_topright', '_bottomleft', '_bottomright', '_top', '_bottom']
bnd_nf = [6, 6, 6, 6, 1, 1]
for bs, nf in zip(bnd_suffix, bnd_nf):
    mycell = 'boundary'+bs 
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    params=deepcopy(params_transistor_default)
    params['nf'] = nf #number of fingers
    params['generate_gate_pins'] = False
    params['generate_sd_pins'] = False
    #params['instance_cellname_list'] = ['_'+header+'_space_base_nf1']*2 
    #params['instance_xy_list'] = [[params['cpo']*4, 0], [params['cpo']*5, 0]]
    construct_mosfet_structure(laygen, **params)

    #momcap generation
    capdim = np.array([21, 3])
    capsp = np.array([0.064, 0.064])
    capwidth = np.array([0.032, 0.032])
    caplayer = [metal[5], metal[6]]
    cap_pinlayer = [pin[5], pin[6]]
    vname = 'via_M5_M6_0'
    #momcap_center generation
    mycell = 'momcap_center_1x' 
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    # prboundary
    laygen.add_rect(None, [[0, 0], (capdim-np.array([1, 1]))*capsp], prbnd)
    for i in range(capdim[0]): #vertical
        if i%2==0: #bottom
            xy0 = np.array([i*capsp[0]-capwidth[0]/2, 0])
            xy1 = np.array([i*capsp[0]+capwidth[0]/2, (capdim[1]-1)*capsp[1]])
            laygen.add_rect(None, [xy0, xy1], caplayer[0])
            for j in range(capdim[1]): #via
                if j%2==0: #bottom
                    xy0 = np.array([i*capsp[0], 0])
                    xy1 = np.array([i*capsp[0], (capdim[1]-1)*capsp[1]])
                    laygen.add_inst(None, workinglib, vname, xy=xy0)
                    laygen.add_inst(None, workinglib, vname, xy=xy1)
    for j in range(capdim[1]): #horizontal
        if j%2==0: #bottom
            xy0 = np.array([0, j*capsp[1]-capwidth[1]/2])
            xy1 = np.array([(capdim[0]-1)*capsp[0], j*capsp[1]+capwidth[1]/2])
            laygen.add_rect(None, [xy0, xy1], caplayer[1])
            if j==0:
                laygen.add_pin('BOTTOM', 'BOTTOM', [xy0, xy1], cap_pinlayer[0])
        else: #top
            xy0 = np.array([0+2*capsp[0], j*capsp[1]-capwidth[1]/2])
            xy1 = np.array([(capdim[0]-1-2)*capsp[0], j*capsp[1]+capwidth[1]/2])
            laygen.add_rect(None, [xy0, xy1], caplayer[1])
            laygen.add_pin('TOP', 'TOP', [xy0, xy1], cap_pinlayer[1])
    #momcap_dmy generation
    mycell = 'momcap_dmy_1x' 
    mycells.append(mycell)
    laygen.add_cell(mycell)
    laygen.sel_cell(mycell)
    # prboundary
    laygen.add_rect(None, [[0, 0], (capdim-np.array([1, 1]))*capsp], prbnd)
    for i in range(capdim[0]): #vertical
        if i%2==0: #bottom
            xy0 = np.array([i*capsp[0]-capwidth[0]/2, 0])
            xy1 = np.array([i*capsp[0]+capwidth[0]/2, (capdim[1]-1)*capsp[1]])
            laygen.add_rect(None, [xy0, xy1], caplayer[0])
            for j in range(capdim[1]): #via
                if j%2==0: #bottom
                    xy0 = np.array([i*capsp[0], 0])
                    xy1 = np.array([i*capsp[0], (capdim[1]-1)*capsp[1]])
                    laygen.add_inst(None, workinglib, vname, xy=xy0)
                    laygen.add_inst(None, workinglib, vname, xy=xy1)
    for j in range(capdim[1]): #horizontal
        if j%2==0: #bottom
            xy0 = np.array([0, j*capsp[1]-capwidth[1]/2])
            xy1 = np.array([(capdim[0]-1)*capsp[0], j*capsp[1]+capwidth[1]/2])
            laygen.add_rect(None, [xy0, xy1], caplayer[1])
    momcap_aux_cells = ['momcap_boundary_1x', 'momcap_dmyblk_1x']+['momcap_dmyptn_m'+str(i)+'_1x' for i in range(1,10)]
    for mycell in momcap_aux_cells:
        mycells.append(mycell)
        laygen.add_cell(mycell)
        laygen.sel_cell(mycell)
        # prboundary
        laygen.add_rect(None, [[0, 0], (capdim-np.array([1, 1]))*capsp], prbnd)


#bag export, if bag does not exist, gds export
from imp import find_module
try:
    find_module('bag')
    #bag export
    print("export to BAG")
    import bag
    prj = bag.BagProject()
    laygen.export_BAG(prj, cellname=mycells)
except ImportError:
    #gds export
    print("export to GDS")
    laygen.export_GDS(workinglib+'.gds', cellname=mycells, layermapfile=tech+".layermap")

