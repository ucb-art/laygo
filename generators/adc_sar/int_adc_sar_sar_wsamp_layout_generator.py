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

"""ADC library
"""
import laygo
import numpy as np
from math import log
import yaml
import os
import laygo.GridLayoutGeneratorHelper as laygenhelper #utility functions
#import logging;logging.basicConfig(level=logging.DEBUG)

def add_to_export_ports(export_ports, pins):
    if type(pins) != list:
        pins = [pins]

    for pin in pins:
        netname = pin.netname
        bbox_float = pin.xy.reshape((1,4))[0]
        for ind in range(len(bbox_float)): # keeping only 3 decimal places
            bbox_float[ind] = float('%.3f' % bbox_float[ind])
        port_entry = dict(layer=int(pin.layer[0][1]), bbox=bbox_float.tolist())
        if netname in export_ports.keys():
            export_ports[netname].append(port_entry)
        else:
            export_ports[netname] = [port_entry]

    return export_ports

def generate_sar_wsamp(laygen, objectname_pfix, workinglib, samp_lib, space_1x_lib, sar_name, samp_name, space_1x_name,
                       placement_grid, routing_grid_m5m6,
                       routing_grid_m5m6_thick, routing_grid_m5m6_thick_basic,
                       num_bits=9, origin=np.array([0, 0])):
    """generate sar with sampling frontend """
    pg = placement_grid

    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic #for clock routing

    # placement
    # sar
    isar=laygen.place(name="I" + objectname_pfix + 'SAR0', templatename=sar_name,
                      gridname=pg, xy=origin, template_libname=workinglib)
    # samp
    isamp = laygen.relplace(name="I" + objectname_pfix + 'SAMP0', templatename=samp_name,
                          gridname=pg, refinstname=isar.name, direction='top', template_libname=samp_lib)
    # manual vref1
    #ivref1=laygen.place(name="I" + objectname_pfix + 'VREF1', templatename='sar_wsamp_vref1_manual',
    #                  gridname=pg, xy=origin, template_libname=workinglib)
    ivref1=laygen.add_inst(None, workinglib, 'sar_wsamp_vref1_manual', xy=np.array([0, 0]))

    #prboundary
    sar_size = laygen.templates.get_template(sar_name, libname=workinglib).size
    samp_size = laygen.templates.get_template(samp_name, libname=samp_lib).size
    space_size = laygen.templates.get_template(space_1x_name, libname=space_1x_lib).size
    #size_x=sar_size[0]
    size_x=sar_size[0]+2.4
    print(laygen.get_inst(ivref1.name, libname=workinglib).size)
    size_y=int((sar_size[1]+samp_size[1])/space_size[1]+1)*space_size[1]
    laygen.add_rect(None, np.array([origin, origin+np.array([size_x, size_y])]), laygen.layers['prbnd'])

    # template handles
    sar_template = laygen.templates.get_template(sar_name, workinglib)
    samp_template = laygen.templates.get_template(samp_name, samp_lib)

    #reference coordinates
    pdict_m5m6=laygen.get_inst_pin_xy(None, None, rg_m5m6)
    pdict_m5m6_thick=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    pdict_m5m6_thick_basic=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick_basic)
    sar_pins=sar_template.pins
    samp_pins=samp_template.pins
    #sar_xy=isar.xy[0]
    #samp_xy=isamp.xy[0]
    sar_xy=isar.xy
    samp_xy=isamp.xy

    # export_dict will be written to a yaml file for using with StdCellBase
    export_dict = {'boundaries': {'lib_name': 'ge_tech_logic_templates',
                                  'lr_width': 8,
                                  'tb_height': 0.5},
                   'cells': {'sar_wsamp': {'cell_name': 'sar_wsamp',
                                                 'lib_name': workinglib,
                                                 'size': [40, 1]}},
                   'spaces': [{'cell_name': 'space_4x',
                               'lib_name': 'ge_tech_logic_templates',
                               'num_col': 4},
                              {'cell_name': 'space_2x',
                               'lib_name': 'ge_tech_logic_templates',
                               'num_col': 2}],
                   'tech_params': {'col_pitch': 0.09,
                                   'directions': ['x', 'y', 'x', 'y'],
                                   'height': 0.96,
                                   'layers': [2, 3, 4, 5],
                                   'spaces': [0.064, 0.05, 0.05, 0.05],
                                   'widths': [0.032, 0.04, 0.04, 0.04]}}
    export_ports = dict()


    #signa lroute (clk/inp/inm)
    #make virtual grids and route on the grids (assuming drc clearance of each block)
    rg_m5m6_thick_basic_temp_sig='route_M5_M6_thick_basic_temp_sig'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m5m6_thick_basic, gridname_output=rg_m5m6_thick_basic_temp_sig,
                                          instname=isamp.name, 
                                          inst_pin_prefix=['ckout', 'outp', 'outn'], xy_grid_type='xgrid')
    pdict_m5m6_thick_basic_temp_sig = laygen.get_inst_pin_xy(None, None, rg_m5m6_thick_basic_temp_sig)
    #clock
    rclk0 = laygen.route(None, laygen.layers['metal'][5],
                         xy0=pdict_m5m6_thick_basic_temp_sig[isamp.name]['ckout'][0],
                         xy1=pdict_m5m6_thick_basic_temp_sig[isar.name]['CLK0'][1]-np.array([0,1]), gridname0=rg_m5m6_thick_basic_temp_sig)
    laygen.via(None,pdict_m5m6_thick_basic_temp_sig[isar.name]['CLK0'][1], rg_m5m6_thick_basic_temp_sig)
    laygen.via(None,pdict_m5m6_thick_basic_temp_sig[isar.name]['CLK1'][1], rg_m5m6_thick_basic_temp_sig)

    #frontend sig
    inp_y_list=[]
    inm_y_list=[]
    for pn, p in pdict_m5m6_thick_basic_temp_sig[isar.name].items():
        if pn.startswith('INP'):
            inp_y_list.append(p[0][1])
            pv=np.array([pdict_m5m6_thick_basic_temp_sig[isamp.name]['outp'][0][0], p[0][1]])
            laygen.via(None,pv, rg_m5m6_thick_basic_temp_sig)
        if pn.startswith('INM'):
            inm_y_list.append(p[0][1])
            pv=np.array([pdict_m5m6_thick_basic_temp_sig[isamp.name]['outn'][0][0], p[0][1]])
            laygen.via(None,pv, rg_m5m6_thick_basic_temp_sig)
    inp_y=min(inp_y_list)
    inm_y=min(inm_y_list)
    rinp0 = laygen.route(None, laygen.layers['metal'][5],
                         xy0=pdict_m5m6_thick_basic_temp_sig[isamp.name]['outp'][0],
                         xy1=np.array([pdict_m5m6_thick_basic_temp_sig[isamp.name]['outp'][0][0],inp_y-1]), 
                         gridname0=rg_m5m6_thick_basic_temp_sig)
    rinm0 = laygen.route(None, laygen.layers['metal'][5],
                         xy0=pdict_m5m6_thick_basic_temp_sig[isamp.name]['outn'][0],
                         xy1=np.array([pdict_m5m6_thick_basic_temp_sig[isamp.name]['outn'][0][0],inm_y-1]), 
                         gridname0=rg_m5m6_thick_basic_temp_sig)
    #rinp0 = laygen.route(None, laygen.layers['metal'][5],
    #                     xy0=pdict_m5m6_thick_basic_temp_sig[isamp.name]['outp'][0],
    #                     xy1=np.array([pdict_m5m6_thick_basic_temp_sig[isar.name]['INP0'][0][0],inp_y-1]), 
    #                     gridname0=rg_m5m6_thick_basic_temp_sig)
    #rinm0 = laygen.route(None, laygen.layers['metal'][5],
    #                     xy0=pdict_m5m6_thick_basic_temp_sig[isamp.name]['outn'][0],
    #                     xy1=np.array([pdict_m5m6_thick_basic_temp_sig[isar.name]['INM0'][0][0],inm_y-1]), 
    #                     gridname0=rg_m5m6_thick_basic_temp_sig)

    #input pins (just duplicate from lower hierarchy cells)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=laygen.get_inst_pin_xy(isamp.name, 'ckin', rg_m3m4)[1]+np.array([-2,0]), 
                 xy1=laygen.get_inst_pin_xy(isamp.name, 'ckin', rg_m3m4)[1]+np.array([-2,6]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    CLK_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='CLK', layer=laygen.layers['pin'][3], size=4, direction="top")
    #CLK_pin=laygen.add_pin('CLK', 'CLK', samp_xy+samp_pins['ckin']['xy'], samp_pins['ckin']['layer'])
    export_ports = add_to_export_ports(export_ports, CLK_pin)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=laygen.get_inst_pin_xy(isamp.name, 'inp', rg_m3m4)[1]+np.array([-1,0]), 
                 xy1=laygen.get_inst_pin_xy(isamp.name, 'inp', rg_m3m4)[1]+np.array([-1,18]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    inp_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='INP', layer=laygen.layers['pin'][3], size=4, direction="top")
    #inp_pin=laygen.add_pin('INP', 'INP', samp_xy+samp_pins['inp']['xy'], samp_pins['ckin']['layer'])
    export_ports = add_to_export_ports(export_ports, inp_pin)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=laygen.get_inst_pin_xy(isamp.name, 'inn', rg_m3m4)[1]+np.array([1,0]), 
                 xy1=laygen.get_inst_pin_xy(isamp.name, 'inn', rg_m3m4)[1]+np.array([1,18]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    inn_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='INM', layer=laygen.layers['pin'][3], size=4, direction="top")
    #inn_pin=laygen.add_pin('INM', 'INM', samp_xy+samp_pins['inn']['xy'], samp_pins['ckin']['layer'])
    export_ports = add_to_export_ports(export_ports, inn_pin)

    #laygen.route(None, laygen.layers['metal'][4],
    #             xy0=laygen.get_inst_pin_xy(isar.name, 'OSP', rg_m3m4)[0]+np.array([0,0]),
    #             xy1=laygen.get_inst_pin_xy(isar.name, 'OSP', rg_m3m4)[0]+np.array([-5,0]), 
    #             via0=[0, 0], gridname0=rg_m3m4)
    #laygen.route(None, laygen.layers['metal'][5],
    #             xy0=laygen.get_inst_pin_xy(isar.name, 'OSP', rg_m4m5)[0]+np.array([-5,0]),
    #             xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'OSP', rg_m4m5)[0][0],0])+np.array([-5,9]), 
    #             via0=[0, 0], via1=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
    #laygen.route(None, laygen.layers['metal'][4],
    #             xy0=np.array([laygen.get_inst_pin_xy(isar.name, 'OSP', rg_m3m4)[0][0],0])+np.array([-5,9]), 
    #             xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'OSP', rg_m3m4)[0][0],0])+np.array([0,9]), 
    #             gridname0=rg_m3m4)
    #rpin=laygen.route(None, laygen.layers['metal'][3],
    #             xy0=np.array([laygen.get_inst_pin_xy(isar.name, 'OSP', rg_m3m4)[0][0],0])+np.array([0,9]), 
    #             xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'OSP', rg_m3m4)[0][0],0])+np.array([0,0]), 
    #             via0=[0, 0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'OSP', rg_m3m4)[0]+np.array([0,0]),
                 xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'SAOP', rg_m3m4)[0][0],laygen.get_inst_pin_xy(isar.name, 'OSP', rg_m3m4)[0][1]]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][5],
                 xy0=np.array([laygen.get_inst_pin_xy(isar.name, 'SAOP', rg_m4m5)[0][0],laygen.get_inst_pin_xy(isar.name, 'OSP', rg_m4m5)[0][1]]),
                 xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'SAOP', rg_m4m5)[0][0],laygen.get_inst_pin_xy(isamp.name, 'ckout', rg_m4m5)[0][1]]), 
                 via0=[0, 0], via1=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
    laygen.route(None, laygen.layers['metal'][4],
                 xy0=np.array([laygen.get_inst_pin_xy(isar.name, 'SAOP', rg_m3m4)[0][0],laygen.get_inst_pin_xy(isamp.name, 'ckout', rg_m3m4)[0][1]]),
                 xy1=np.array([laygen.get_inst_pin_xy(isamp.name, 'inp', rg_m3m4)[0][0]-24,laygen.get_inst_pin_xy(isamp.name, 'ckout', rg_m3m4)[0][1]]), 
                 gridname0=rg_m3m4)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=np.array([laygen.get_inst_pin_xy(isamp.name, 'inp', rg_m3m4)[0][0]-24,laygen.get_inst_pin_xy(isamp.name, 'ckout', rg_m3m4)[0][1]]), 
                 xy1=laygen.get_inst_pin_xy(isamp.name, 'inp', rg_m3m4)[1]+np.array([-24,18]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    osp_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='OSP', layer=laygen.layers['pin'][3], size=4, direction="top")
    #osp_pin=laygen.add_pin('OSP', 'OSP', sar_xy+sar_pins['OSP']['xy'], sar_pins['OSP']['layer'])
    export_ports = add_to_export_ports(export_ports, osp_pin)
    #laygen.route(None, laygen.layers['metal'][4],
    #             xy0=laygen.get_inst_pin_xy(isar.name, 'OSM', rg_m3m4)[0]+np.array([0,0]),
    #             xy1=laygen.get_inst_pin_xy(isar.name, 'OSM', rg_m3m4)[0]+np.array([4,0]), 
    #             via0=[0, 0], gridname0=rg_m3m4)
    #laygen.route(None, laygen.layers['metal'][5],
    #             xy0=laygen.get_inst_pin_xy(isar.name, 'OSM', rg_m4m5)[0]+np.array([4,0]),
    #             xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'OSM', rg_m4m5)[0][0],0])+np.array([4,9]), 
    #             via0=[0, 0], via1=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
    #laygen.route(None, laygen.layers['metal'][4],
    #             xy0=np.array([laygen.get_inst_pin_xy(isar.name, 'OSM', rg_m3m4)[0][0],0])+np.array([4,9]), 
    #             xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'OSM', rg_m3m4)[0][0],0])+np.array([0,9]), 
    #             gridname0=rg_m3m4)
    #rpin=laygen.route(None, laygen.layers['metal'][3],
    #             xy0=np.array([laygen.get_inst_pin_xy(isar.name, 'OSM', rg_m3m4)[0][0],0])+np.array([0,9]), 
    #             xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'OSM', rg_m3m4)[0][0],0])+np.array([0,0]), 
    #             via0=[0, 0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'OSM', rg_m3m4)[0]+np.array([0,0]),
                 xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<1>', rg_m3m4)[0][0]+5,laygen.get_inst_pin_xy(isar.name, 'OSM', rg_m3m4)[0][1]]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][5],
                 xy0=np.array([laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<1>', rg_m4m5)[0][0]+5,laygen.get_inst_pin_xy(isar.name, 'OSM', rg_m4m5)[0][1]]),
                 xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<1>', rg_m4m5)[0][0]+5,laygen.get_inst_pin_xy(isamp.name, 'ckout', rg_m4m5)[0][1]]), 
                 via0=[0, 0], via1=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
    laygen.route(None, laygen.layers['metal'][4],
                 xy0=np.array([laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<1>', rg_m3m4)[0][0]+5,laygen.get_inst_pin_xy(isamp.name, 'ckout', rg_m3m4)[0][1]]),
                 xy1=np.array([laygen.get_inst_pin_xy(isamp.name, 'inn', rg_m3m4)[0][0]+24,laygen.get_inst_pin_xy(isamp.name, 'ckout', rg_m3m4)[0][1]]), 
                 gridname0=rg_m3m4)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=np.array([laygen.get_inst_pin_xy(isamp.name, 'inn', rg_m3m4)[0][0]+24,laygen.get_inst_pin_xy(isamp.name, 'ckout', rg_m3m4)[0][1]]), 
                 xy1=laygen.get_inst_pin_xy(isamp.name, 'inn', rg_m3m4)[1]+np.array([24,18]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    osn_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='OSM', layer=laygen.layers['pin'][3], size=4, direction="top")
    #osn_pin=laygen.add_pin('OSM', 'OSM', sar_xy+sar_pins['OSM']['xy'], sar_pins['OSM']['layer'])
    export_ports = add_to_export_ports(export_ports, osn_pin)
    # For fader, VREF2=VDD, VREF0=VSS
    for pn, p in sar_pins.items():
        if pn.startswith('VREF<0>'):
            pxy=sar_xy+sar_pins[pn]['xy']
            #vref0_pin=laygen.add_pin(pn, 'VREF<0>', pxy, sar_pins[pn]['layer'])
            laygen.via(None, xy=np.array([2, 0]), gridname=rg_m5m6_thick, refinstname=isar.name, refpinname=pn)
            #export_ports = add_to_export_ports(export_ports, vref0_pin)
        if pn.startswith('VREF<1>'):
            pxy=sar_xy+sar_pins[pn]['xy']
            #vref1_pin=laygen.add_pin(pn, 'VREF<1>', pxy, sar_pins[pn]['layer'])
            #export_ports = add_to_export_ports(export_ports, vref1_pin)
        if pn.startswith('VREF<2>'):
            pxy=sar_xy+sar_pins[pn]['xy']
            #vref2_pin=laygen.add_pin(pn, 'VREF<2>', pxy, sar_pins[pn]['layer'])
            laygen.via(None, xy=np.array([1, 0]), gridname=rg_m5m6_thick, refinstname=isar.name, refpinname=pn)
            #export_ports = add_to_export_ports(export_ports, vref2_pin)
    #laygen.add_pin('VREF_M5R<2>', 'VREF<2>', sar_xy+sar_pins['VREF_M5R<2>']['xy'], sar_pins['VREF_M5R<2>']['layer'])
    #laygen.add_pin('VREF_M5R<1>', 'VREF<1>', sar_xy+sar_pins['VREF_M5R<1>']['xy'], sar_pins['VREF_M5R<1>']['layer'])
    #laygen.add_pin('VREF_M5R<0>', 'VREF<0>', sar_xy+sar_pins['VREF_M5R<0>']['xy'], sar_pins['VREF_M5R<0>']['layer'])
    #laygen.add_pin('VREF_M5L<2>', 'VREF<2>', sar_xy+sar_pins['VREF_M5L<2>']['xy'], sar_pins['VREF_M5L<2>']['layer'])
    #laygen.add_pin('VREF_M5L<1>', 'VREF<1>', sar_xy+sar_pins['VREF_M5L<1>']['xy'], sar_pins['VREF_M5L<1>']['layer'])
    #laygen.add_pin('VREF_M5L<0>', 'VREF<0>', sar_xy+sar_pins['VREF_M5L<0>']['xy'], sar_pins['VREF_M5L<0>']['layer'])
    laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CKDSEL0<1>', rg_m4m5)[0]+np.array([0,9]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CKDSEL0<1>', rg_m4m5)[0]+np.array([4,9]), 
                 via0=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CKDSEL0<1>', rg_m3m4)[0]+np.array([4,9]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CKDSEL0<1>', rg_m3m4)[0]+np.array([4,0]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    ckd01_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='CKDSEL0<1>', layer=laygen.layers['pin'][3], size=4, direction="bottom")
    #ckd01_pin=laygen.add_pin('CKDSEL0<1>', 'CKDSEL0<1>', sar_xy+sar_pins['CKDSEL0<1>']['xy'], sar_pins['CKDSEL0<1>']['layer'])
    export_ports = add_to_export_ports(export_ports, ckd01_pin)
    laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CKDSEL0<0>', rg_m4m5)[0]+np.array([0,8]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CKDSEL0<0>', rg_m4m5)[0]+np.array([4,8]), 
                 via0=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CKDSEL0<0>', rg_m3m4)[0]+np.array([4,8]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CKDSEL0<0>', rg_m3m4)[0]+np.array([4,0]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    ckd00_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='CKDSEL0<0>', layer=laygen.layers['pin'][3], size=4, direction="bottom")
    #ckd00_pin=laygen.add_pin('CKDSEL0<0>', 'CKDSEL0<0>', sar_xy+sar_pins['CKDSEL0<0>']['xy'], sar_pins['CKDSEL0<0>']['layer'])
    export_ports = add_to_export_ports(export_ports, ckd00_pin)
    laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<1>', rg_m4m5)[0]+np.array([0,5]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<1>', rg_m4m5)[0]+np.array([4,5]), 
                 via0=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<1>', rg_m3m4)[0]+np.array([4,5]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<1>', rg_m3m4)[0]+np.array([4,0]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    ckd11_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='CKDSEL1<1>', layer=laygen.layers['pin'][3], size=4, direction="bottom")
    #ckd11_pin=laygen.add_pin('CKDSEL1<1>', 'CKDSEL1<1>', sar_xy+sar_pins['CKDSEL1<1>']['xy'], sar_pins['CKDSEL1<1>']['layer'])
    export_ports = add_to_export_ports(export_ports, ckd11_pin)
    laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<0>', rg_m4m5)[0]+np.array([0,6]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<0>', rg_m4m5)[0]+np.array([4,6]), 
                 via0=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<0>', rg_m3m4)[0]+np.array([4,6]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CKDSEL1<0>', rg_m3m4)[0]+np.array([4,0]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    ckd10_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='CKDSEL1<0>', layer=laygen.layers['pin'][3], size=4, direction="bottom")
    #ckd10_pin=laygen.add_pin('CKDSEL1<0>', 'CKDSEL1<0>', sar_xy+sar_pins['CKDSEL1<0>']['xy'], sar_pins['CKDSEL1<0>']['layer'])
    export_ports = add_to_export_ports(export_ports, ckd10_pin)
    #laygen.add_pin('EXTCLK', 'EXTCLK', sar_xy+sar_pins['EXTCLK']['xy'], sar_pins['EXTCLK']['layer'])
    laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'EXTSEL_CLK', rg_m4m5)[0]+np.array([0,6]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'EXTSEL_CLK', rg_m4m5)[0]+np.array([4,6]), 
                 via0=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'EXTSEL_CLK', rg_m3m4)[0]+np.array([4,6]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'EXTSEL_CLK', rg_m3m4)[0]+np.array([4,0]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    extsel_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='EXTSEL_CLK', layer=laygen.layers['pin'][3], size=4, direction="bottom")
    #extsel_pin=laygen.add_pin('EXTSEL_CLK', 'EXTSEL_CLK', sar_xy+sar_pins['EXTSEL_CLK']['xy'], sar_pins['EXTSEL_CLK']['layer'])
    export_ports = add_to_export_ports(export_ports, extsel_pin)
    #output pins (just duplicate from lower hierarchy cells)
    for i in range(num_bits):
        pn='ADCOUT'+'<'+str(i)+'>'
        laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(isar.name, pn, rg_m4m5)[0]+np.array([0,5+i]),
                 xy1=laygen.get_inst_pin_xy(isar.name, pn, rg_m4m5)[0]+np.array([4,5+i]), 
                 via0=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
        rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=laygen.get_inst_pin_xy(isar.name, pn, rg_m3m4)[0]+np.array([4,5+i]),
                 xy1=laygen.get_inst_pin_xy(isar.name, pn, rg_m3m4)[0]+np.array([4,0]), 
                 via0=[0, 0], gridname0=rg_m3m4)
        adcout_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name=pn, layer=laygen.layers['pin'][3], size=4, direction="bottom")
        #laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
        export_ports = add_to_export_ports(export_ports, adcout_pin)
    laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CLKOUT0', rg_m4m5)[0]+np.array([0,6]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CLKOUT0', rg_m4m5)[0]+np.array([4,6]), 
                 via0=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CLKOUT0', rg_m3m4)[0]+np.array([4,6]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CLKOUT0', rg_m3m4)[0]+np.array([4,0]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    clko0_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='CLKO0', netname='CLKO', layer=laygen.layers['pin'][3], size=4, direction="bottom")
    #clko0_pin=laygen.add_pin('CLKO0', 'CLKO', sar_xy+sar_pins['CLKOUT0']['xy'], sar_pins['CLKOUT0']['layer'])
    export_ports = add_to_export_ports(export_ports, clko0_pin)
    laygen.route(None, laygen.layers['metal'][4],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CLKOUT1', rg_m4m5)[0]+np.array([0,8]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CLKOUT1', rg_m4m5)[0]+np.array([4,8]), 
                 via0=[0, 0], endstyle1="extend", gridname0=rg_m4m5)
    rpin=laygen.route(None, laygen.layers['metal'][3],
                 xy0=laygen.get_inst_pin_xy(isar.name, 'CLKOUT1', rg_m3m4)[0]+np.array([4,8]),
                 xy1=laygen.get_inst_pin_xy(isar.name, 'CLKOUT1', rg_m3m4)[0]+np.array([4,0]), 
                 via0=[0, 0], gridname0=rg_m3m4)
    clko1_pin=laygen.boundary_pin_from_rect(rpin, gridname=rg_m3m4, name='CLKO2', netname='CLKO', layer=laygen.layers['pin'][3], size=4, direction="bottom")
    #clko1_pin=laygen.add_pin('CLKO1', 'CLKO', sar_xy+sar_pins['CLKOUT1']['xy'], sar_pins['CLKOUT1']['layer'])
    export_ports = add_to_export_ports(export_ports, clko1_pin)
    #laygen.add_pin('CLKO2', 'CLKO', sar_xy+sar_pins['CLKOUT2']['xy'], sar_pins['CLKOUT2']['layer'])
    
    '''
    #probe pins
    laygen.add_pin('CLK0', 'ICLK', sar_xy+sar_pins['CLK0']['xy'], sar_pins['CLK0']['layer'])
    laygen.add_pin('CLK1', 'ICLK', sar_xy+sar_pins['CLK1']['xy'], sar_pins['CLK1']['layer'])
    #laygen.add_pin('CLK2', 'ICLK', sar_xy+sar_pins['CLK2']['xy'], sar_pins['CLK2']['layer'])
    laygen.add_pin('CLKPRB_SAMP', 'CLKPRB_SAMP', samp_xy+samp_pins['ckpg']['xy'], samp_pins['ckpg']['layer'])
    #laygen.add_pin('CLKPRB_SAR', 'CLKPRB_SAR', sar_xy+sar_pins['CLKPRB']['xy'], sar_pins['CLKPRB']['layer'])
    laygen.add_pin('SAMPP', 'SAMPP', sar_xy+sar_pins['SAINP']['xy'], sar_pins['SAINP']['layer'])
    laygen.add_pin('SAMPM', 'SAMPM', sar_xy+sar_pins['SAINM']['xy'], sar_pins['SAINM']['layer'])
    laygen.add_pin('SAOP', 'SAOP', sar_xy+sar_pins['SAOP']['xy'], sar_pins['SAOP']['layer'])
    laygen.add_pin('SAOM', 'SAOM', sar_xy+sar_pins['SAOM']['xy'], sar_pins['SAOM']['layer'])
    laygen.add_pin('SARCLK', 'SARCLK', sar_xy+sar_pins['SARCLK']['xy'], sar_pins['SARCLK']['layer'])
    laygen.add_pin('SARCLKB', 'SARCLKB', sar_xy+sar_pins['SARCLKB']['xy'], sar_pins['SARCLKB']['layer'])
    #laygen.add_pin('COMPOUT', 'COMPOUT', sar_xy+sar_pins['COMPOUT']['xy'], sar_pins['COMPOUT']['layer'])
    laygen.add_pin('DONE', 'DONE', sar_xy+sar_pins['DONE']['xy'], sar_pins['DONE']['layer'])
    laygen.add_pin('UP', 'UP', sar_xy+sar_pins['UP']['xy'], sar_pins['UP']['layer'])
    laygen.add_pin('PHI0', 'PHI0', sar_xy+sar_pins['PHI0']['xy'], sar_pins['PHI0']['layer'])
    for i in range(num_bits):
        pn='ZP'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
        pn='ZMID'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
        pn='ZM'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
        pn='SB'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
    for i in range(num_bits-1):
        pn='VOL'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
        pn='VOR'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
    '''

    #VDD/VSS pin
    vddcnt=0
    vsscnt=0
    for p in pdict_m5m6[isar.name]:
        if p.startswith('VDD'):
            xy0=pdict_m5m6_thick[isar.name][p]
            vdd_pin=laygen.pin(name='VDDSAR' + str(vddcnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VDDSAR')
            vddcnt+=1
            export_ports = add_to_export_ports(export_ports, vdd_pin)
        if p.startswith('VSS'):
            xy0=pdict_m5m6_thick[isar.name][p]
            vss_pin=laygen.pin(name='VSSSAR' + str(vsscnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VSS:')
            vsscnt+=1
            export_ports = add_to_export_ports(export_ports, vss_pin)
    #extract VDD/VSS grid from samp and make power pins
    rg_m5m6_thick_temp_samp='route_M5_M6_thick_temp_samp'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_samp,
                                          instname=isamp.name, 
                                          inst_pin_prefix=['VDD', 'VSS'], xy_grid_type='ygrid')
    pdict_m5m6_thick_temp_samp = laygen.get_inst_pin_xy(None, None, rg_m5m6_thick_temp_samp)
    vddcnt=0
    vsscnt=0
    for p in pdict_m5m6_thick_temp_samp[isamp.name]:
        if p.startswith('VDD'):
            xy0=pdict_m5m6_thick_temp_samp[isamp.name][p]
            vddsamp_pin=laygen.pin(name='VDDSAMP' + str(vddcnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick_temp_samp, netname='VDDSAMP')
            vddcnt+=1
            export_ports = add_to_export_ports(export_ports, vddsamp_pin)
        if p.startswith('VSS'):
            xy0=pdict_m5m6_thick_temp_samp[isamp.name][p]
            vsssamp_pin=laygen.pin(name='VSSSAMP' + str(vsscnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick_temp_samp, netname='VSS:')
            vsscnt+=1
            export_ports = add_to_export_ports(export_ports, vsssamp_pin)

    export_dict['cells']['sar_wsamp']['ports'] = export_ports
    export_dict['cells']['sar_wsamp']['size_um'] = [float(int(size_x*1e3))/1e3, float(int(size_y*1e3))/1e3]
    #export_dict['cells']['clk_dis_N_units']['num_ways'] = num_ways
    # print('export_dict:')
    # pprint(export_dict)
    # save_path = path.dirname(path.dirname(path.realpath(__file__))) + '/dsn_scripts/'
    save_path = workinglib 
    #if path.isdir(save_path) == False:
    #    mkdir(save_path)
    with open(save_path + '_int.yaml', 'w') as f:
        yaml.dump(export_dict, f, default_flow_style=False)


if __name__ == '__main__':
    laygen = laygo.GridLayoutGenerator(config_file="laygo_config.yaml")

    import imp
    try:
        imp.find_module('bag')
        laygen.use_phantom = False
    except ImportError:
        laygen.use_phantom = True

    tech=laygen.tech
    utemplib = tech+'_microtemplates_dense'
    logictemplib = tech+'_logic_templates'
    samp_lib = 'adc_sampler_ec'
    samp_name = 'sampler_nmos'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    #library load or generation
    workinglib = 'adc_sar_generated'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    if os.path.exists(workinglib+'.yaml'): #generated layout file exists
        laygen.load_template(filename=workinglib+'.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #grid
    pg = 'placement_basic' #placement grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m1m2_thick = 'route_M1_M2_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m5m6_basic_thick = 'route_M5_M6_basic_thick'
    rg_m5m6_thick_basic = 'route_M5_M6_thick_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    num_bits=9
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        num_bits=specdict['n_bit']
        if specdict['samp_use_laygo'] is True:
            samp_lib = 'adc_sar_generated'
            samp_name = 'sarsamp'
        else:
            laygen.load_template(filename=samp_lib+'.yaml', libname=samp_lib)
    #yamlfile_system_input="adc_sar_dsn_system_input.yaml"
    #if load_from_file==True:
    #    with open(yamlfile_system_input, 'r') as stream:
    #        sysdict_i = yaml.load(stream)
    #    num_bits=sysdict_i['n_bit']
    #sar generation
    cellname='sar_wsamp' #_'+str(num_bits)+'b'
    sar_name = 'sar' #_'+str(num_bits)+'b'
    space_1x_name = 'space_1x'

    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sar_wsamp(laygen, objectname_pfix='SA0', workinglib=workinglib, samp_lib=samp_lib, space_1x_lib=logictemplib, sar_name=sar_name, samp_name=samp_name, space_1x_name=space_1x_name,
                       placement_grid=pg, routing_grid_m5m6=rg_m5m6, routing_grid_m5m6_thick=rg_m5m6_thick, routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic, 
                       num_bits=num_bits, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    

    laygen.save_template(filename=workinglib+'.yaml', libname=workinglib)
    #bag export, if bag does not exist, gds export
    import imp
    try:
        imp.find_module('bag')
        import bag
        prj = bag.BagProject()
        for mycell in mycell_list:
            laygen.sel_cell(mycell)
            laygen.export_BAG(prj, array_delimiter=['[', ']'])
    except ImportError:
        laygen.export_GDS('output.gds', cellname=mycell_list, layermapfile=tech+".layermap")  # change layermapfile
