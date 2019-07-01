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

def generate_sarbias_top(laygen, objectname_pfix, rdac_libname, sf_libname,
                         rdac_name, sf_name, 
                         placement_grid,
                         routing_grid_m3m4, 
                         routing_grid_m4m5, 
                         routing_grid_m4m5_thick, 
                         routing_grid_m4m5_basic_thick, 
                         routing_grid_m5m6_thick, 
                         routing_grid_m5m6_basic_thick, 
                         routing_grid_m6m7_thick, 
                         num_bias=3, num_rdac=4, num_slice=8, origin=np.array([0, 0])):
    """generate bias top core """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_thick = routing_grid_m4m5_thick
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m6m7_thick = routing_grid_m6m7_thick

    # placement
    # rdac 
    irdac = laygen.place(name="I" + objectname_pfix + 'RDAC0', templatename=rdac_name,
                         gridname=pg, xy=origin, template_libname=rdac_libname)
    isf = laygen.relplace(name="I" + objectname_pfix + 'SF0', templatename=sf_name,
                         gridname=pg, refinstname=irdac.name, template_libname=sf_libname)
    # pin informations (physical)
    rdac_template = laygen.templates.get_template(rdac_name, rdac_libname)
    rdac_size = rdac_template.size
    rdac_pins=rdac_template.pins
    rdac_xy=irdac.xy[0]
    sf_template = laygen.templates.get_template(sf_name, sf_libname)
    sf_size = sf_template.size
    sf_pins=sf_template.pins
    sf_xy=isf.xy
    # VDD/VSS
    x1=sf_xy[0]+sf_pins['VDDRDCAPU_M80']['xy'][1][0]
    for pn in rdac_pins:
        if pn.startswith('VDD'):
            rxy=rdac_xy+np.array([rdac_pins[pn]['xy'][0], [x1, rdac_pins[pn]['xy'][1][1]]])
            laygen.add_rect(None, rxy, laygen.layers['metal'][8])
            laygen.add_pin(pn, 'VDD', rxy, rdac_pins[pn]['layer'])
        if pn.startswith('VSS'):
            rxy=rdac_xy+np.array([rdac_pins[pn]['xy'][0], [x1, rdac_pins[pn]['xy'][1][1]]])
            laygen.add_rect(None, rxy, laygen.layers['metal'][8])
            laygen.add_pin(pn, 'VSS', rxy, rdac_pins[pn]['layer'])
    #pins - code
    pinmap_code=[]
    for i in range(num_bias):
        pinmap_code+=['REF'+str(num_bias-1-i)+'<'+str(8-1-j)+'>' for j in range(8)]
    for i in range(num_slice):
        pinmap_code+=['OSP'+str(num_slice-1-i)+'<'+str(8-1-j)+'>' for j in range(8)]
    for i in range(num_slice):
        pinmap_code+=['OSM'+str(num_slice-1-i)+'<'+str(8-1-j)+'>' for j in range(8)]
    pinmap_code+=['DUM0<'+str(8-1-j)+'>' for j in range(8)]
    for i in range(num_rdac):
        for j in range(40):
            pn=pinmap_code[i*40+j]
            pn_orig='code'+str(i)+'<'+str(39-j)+'>'
            laygen.add_pin(pn, pn, rdac_xy+rdac_pins[pn_orig]['xy'], rdac_pins[pn_orig]['layer'])
    #pins - adcbias
    for pn in sf_pins:
        if pn.startswith('ADCBIAS'):
            pxy=sf_xy+sf_pins[pn]['xy']
            laygen.add_pin(pn, sf_pins[pn]['netname'], pxy, sf_pins[pn]['layer'])
    #laygen.add_pin('ADCBIAS', 'ADCBIAS', sf_xy+sf_pins['ADCBIAS0']['xy'], sf_pins['ADCBIAS0']['layer'])
    #pins - vrefin, osp, osm
    pinmap_out=[None, None, None]
    pinmap_out+=['VOSP'+str(num_slice-1-j) for j in range(num_slice)]
    pinmap_out+=['VOSM'+str(num_slice-1-j) for j in range(num_slice)]
    pinmap_out+=['VDUM0']
    pdict = laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    xy0=np.array([pdict[isf.name]['VREF1<'+str(num_bias-1)+'>'][0][0]+4, pdict[irdac.name]['out0<0>'][0][1]-8])
    for i in range(num_rdac):
        for j in range(5):
            if i==0 and j<3:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5], pdict[irdac.name]['out0<'+str(4-j)+'>'][0], pdict[isf.name]['VIN0<'+str(2-j)+'>'][0], gridname=rg_m5m6_thick)
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5], pdict[irdac.name]['out0<'+str(4-j)+'>'][0], pdict[isf.name]['VIN1<'+str(2-j)+'>'][0], gridname=rg_m5m6_thick)
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5], pdict[irdac.name]['out0<'+str(4-j)+'>'][0], pdict[isf.name]['VIN2<'+str(2-j)+'>'][0], gridname=rg_m5m6_thick)
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5], pdict[irdac.name]['out0<'+str(4-j)+'>'][0], pdict[isf.name]['VIN3<'+str(2-j)+'>'][0], gridname=rg_m5m6_thick)
            else:
                if not pinmap_out[i*5+j].startswith('VDUM'):
                    rh0, rv0 = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5], pdict[irdac.name]['out'+str(i)+'<'+str(4-j)+'>'][0], xy0, gridname=rg_m5m6_thick)
                    xy0=xy0+np.array([1,0])
                    laygen.boundary_pin_from_rect(rv0, rg_m5m6_thick, pinmap_out[i*5+j], laygen.layers['pin'][5], size=6, direction='bottom')
    #pins - VREF
    for i in range(num_bias):
        laygen.add_pin('VREF0<'+str(i)+'>', 'VREF<'+str(i)+'>', sf_xy+sf_pins['VREF0<'+str(i)+'>']['xy'], sf_pins['VREF0<'+str(i)+'>']['layer'])
        laygen.add_pin('VREF1<'+str(i)+'>', 'VREF<'+str(i)+'>', sf_xy+sf_pins['VREF1<'+str(i)+'>']['xy'], sf_pins['VREF1<'+str(i)+'>']['layer'])
        laygen.add_pin('VREF2<'+str(i)+'>', 'VREF<'+str(i)+'>', sf_xy+sf_pins['VREF2<'+str(i)+'>']['xy'], sf_pins['VREF2<'+str(i)+'>']['layer'])
        laygen.add_pin('VREF3<'+str(i)+'>', 'VREF<'+str(i)+'>', sf_xy+sf_pins['VREF3<'+str(i)+'>']['xy'], sf_pins['VREF3<'+str(i)+'>']['layer'])
                

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
    rg_m3m4_thick = 'route_M3_M4_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m4m5_basic_thick = 'route_M4_M5_basic_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m5m6_basic_thick = 'route_M5_M6_basic_thick'
    rg_m6m7_thick = 'route_M6_M7_thick'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    num_bits=9
    num_slices=9
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        num_bits=specdict['n_bit']
        num_slices=specdict['n_interleave']

    cellname = 'sarbias_top_'+str(num_slices)+'slice'
    sf_name = 'sarbias_'+str(num_slices)+'slice_sfarray'
    rdac_name = 'sarbias_'+str(num_slices)+'slice_rdacarray'

    #generation
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarbias_top(laygen, objectname_pfix='BIAS0', 
                    rdac_libname=workinglib, sf_libname=workinglib, 
                    rdac_name=rdac_name, sf_name=sf_name, 
                    placement_grid=pg, 
                    routing_grid_m3m4=rg_m3m4, 
                    routing_grid_m4m5=rg_m4m5, 
                    routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick, 
                    routing_grid_m4m5_thick=rg_m4m5_thick, 
                    routing_grid_m5m6_thick=rg_m5m6_thick, 
                    routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick, 
                    routing_grid_m6m7_thick=rg_m6m7_thick, 
                    num_bias=3, num_rdac=4, origin=np.array([0, 0]))
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
