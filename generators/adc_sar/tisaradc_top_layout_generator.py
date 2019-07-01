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

def generate_tisaradc_top(laygen, objectname_pfix, tisar_libname, bias_libname,
                          tisar_name, bias_name, 
                          placement_grid,
                          routing_grid_m2m3, 
                          routing_grid_m3m4, 
                          routing_grid_m4m5, 
                          routing_grid_m5m6_thick, 
                          num_slice=8, origin=np.array([0, 0])):
    """generate tisar top """
    pg = placement_grid
    rg_m2m3 = routing_grid_m2m3 
    rg_m3m4 = routing_grid_m3m4 
    rg_m4m5 = routing_grid_m4m5 
    rg_m5m6_thick = routing_grid_m5m6_thick
    num_vref_routes=4

    # placement
    ibias = laygen.place(name="I" + objectname_pfix + 'BIAS0', templatename=bias_name,
                         gridname=pg, xy=origin, template_libname=bias_libname)
    bias_size_pg=laygen.get_template_size(ibias.cellname, gridname=pg, libname=workinglib)
    itisar = laygen.place(name="I" + objectname_pfix + 'TISAR0', templatename=tisar_name,
                         gridname=pg, xy=origin+np.array([bias_size_pg[0], 0]), template_libname=tisar_libname)
    tisar_size_pg=laygen.get_template_size(itisar.cellname, gridname=pg, libname=workinglib)
    # placement - clkgbuf
    clkgbuf_size_pg=laygen.get_template_size('clkgcalbuf_wbnd', gridname=pg, libname=workinglib)
    clkgbuf_xy=origin+np.array([bias_size_pg[0], 0])+tisar_size_pg-2*np.array([clkgbuf_size_pg[0], 0])
    iclkgbuf = laygen.place(name="I" + objectname_pfix + 'CLKGBUF0', templatename='clkgcalbuf_wbnd',
                            gridname=pg, xy=clkgbuf_xy, template_libname=workinglib)
    # manual eco
    laygen.add_inst(None, workinglib, 'tisaradc_top_manual', xy=np.array([0, 0]))

    bias_template = laygen.templates.get_template(bias_name, bias_libname)
    bias_size = bias_template.size
    bias_pins=bias_template.pins
    bias_xy=ibias.xy
    tisar_template = laygen.templates.get_template(tisar_name, tisar_libname)
    tisar_size = tisar_template.size
    tisar_pins=tisar_template.pins
    tisar_xy=itisar.xy
    # VDD/VSS
    x0=bias_xy[0]+bias_pins['VDDRDCAPU_M80']['xy'][0][0]
    for pn in tisar_pins:
        if pn.startswith('VDDSAR'):
            rxy=tisar_xy+tisar_pins[pn]['xy']
            rxy[0][0]=x0
            laygen.add_rect(None, rxy, laygen.layers['metal'][8])
            laygen.add_pin(pn, 'VDDADC', rxy, tisar_pins[pn]['layer'])
        if pn.startswith('VDDSAMP'):
            rxy=tisar_xy+tisar_pins[pn]['xy']
            rxy[0][0]=x0
            laygen.add_rect(None, rxy, laygen.layers['metal'][8])
            laygen.add_pin(pn, 'VDDHADC', rxy, tisar_pins[pn]['layer'])
        if pn.startswith('VSS_SAMP_M8') or pn.startswith('VSS_SAR_M8') or pn.startswith('VSS_CLKD_M8'):
            rxy=tisar_xy+tisar_pins[pn]['xy']
            rxy[0][0]=x0
            laygen.add_rect(None, rxy, laygen.layers['metal'][8])
            laygen.add_pin(pn, 'VSS', rxy, tisar_pins[pn]['layer'])
        if pn.startswith('VSS_SAR_M7'):
            rxy=tisar_xy+tisar_pins[pn]['xy']
            laygen.add_pin(pn, 'VSS', rxy, tisar_pins[pn]['layer'])
    #internal connections
    connmap_bias=[]
    connmap_tisar=[]
    for i in range(num_slice):
        connmap_bias+=['VOSP'+str(i)]
        connmap_tisar+=['OSP'+str(i)]
        connmap_bias+=['VOSM'+str(i)]
        connmap_tisar+=['OSM'+str(i)]
    for i in range(num_vref_routes):
        connmap_bias+=['VREF0<'+str(j)+'>' for j in range(3)]
        connmap_tisar+=['VREF'+str(i)+'<'+str(j)+'>' for j in range(3)]
        connmap_bias+=['VREF1<'+str(j)+'>' for j in range(3)]
        connmap_tisar+=['VREF'+str(i)+'<'+str(j)+'>' for j in range(3)]
        connmap_bias+=['VREF2<'+str(j)+'>' for j in range(3)]
        connmap_tisar+=['VREF'+str(i)+'<'+str(j)+'>' for j in range(3)]
        connmap_bias+=['VREF3<'+str(j)+'>' for j in range(3)]
        connmap_tisar+=['VREF'+str(i)+'<'+str(j)+'>' for j in range(3)]
    pdict=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    for i, cnb in enumerate(connmap_bias):
        cnt=connmap_tisar[i]
        rv0, rh0 = laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                   pdict[ibias.name][cnb][0], pdict[itisar.name][cnt][0],
                                   gridname0=rg_m5m6_thick)
    #pins
    for pn in bias_pins:
        if pn.startswith('ADCBIAS'):
            pxy=bias_xy+bias_pins[pn]['xy']
            laygen.add_pin(pn, bias_pins[pn]['netname'], pxy, bias_pins[pn]['layer'])
    pinmap_bias_internal=[]
    pinmap_bias_external=[]
    for i in range(num_slice):
        pinmap_bias_internal+=['OSP'+str(i)+'<'+str(j)+'>' for j in range(8)]
        pinmap_bias_external+=['osp'+str(i)+'<'+str(j)+'>' for j in range(8)]
        pinmap_bias_internal+=['OSM'+str(i)+'<'+str(j)+'>' for j in range(8)]
        pinmap_bias_external+=['osm'+str(i)+'<'+str(j)+'>' for j in range(8)]
    for i in range(3):
        pinmap_bias_internal+=['REF'+str(i)+'<'+str(j)+'>' for j in range(8)]
        pinmap_bias_external+=['vref'+str(i)+'<'+str(j)+'>' for j in range(8)]
    pinmap_bias_internal+=['DUM0<'+str(j)+'>' for j in range(8)]
    pinmap_bias_external+=['clkgbias<'+str(j)+'>' for j in range(8)]
    for i, pnint in enumerate(pinmap_bias_internal):
        pnext=pinmap_bias_external[i]
        laygen.add_pin(pnext, pnext, bias_xy+bias_pins[pnint]['xy'], bias_pins[pnint]['layer'])
    pinmap_tisar_internal=[]
    pinmap_tisar_external=[]
    for i in range(4):
        pinmap_tisar_internal+=['INP0']
        pinmap_tisar_external+=['ADCINP']
        pinmap_tisar_internal+=['INM0']
        pinmap_tisar_external+=['ADCINM']
    for i in range(num_slice):
        pinmap_tisar_internal+=['ASCLKD'+str(i)+'<'+str(j)+'>' for j in range(4)]
        pinmap_tisar_external+=['asclkd'+str(i)+'<'+str(j)+'>' for j in range(4)]
        pinmap_tisar_internal+=['EXTSEL_CLK'+str(i)]
        pinmap_tisar_external+=['extsel_clk'+str(i)]
        pinmap_tisar_internal+=['ADCOUT'+str(i)+'<'+str(j)+'>' for j in range(num_bits)]
        pinmap_tisar_external+=['adcout'+str(i)+'<'+str(j)+'>' for j in range(num_bits)]
    pinmap_tisar_internal+=['CLKOUT_DES']
    pinmap_tisar_external+=['clkout_des']
    # pinmap_tisar_internal+=['CLKBOUT_NC']
    # pinmap_tisar_external+=['clkbout_nc']
    for i, pnint in enumerate(pinmap_tisar_internal):
        pnext=pinmap_tisar_external[i]
        laygen.add_pin(pnext, pnext, tisar_xy+tisar_pins[pnint]['xy'], tisar_pins[pnint]['layer'])
    #clkcal
    pdict_m2m3 = laygen.get_inst_pin_xy(None, None, rg_m2m3)
    pdict_m3m4 = laygen.get_inst_pin_xy(None, None, rg_m3m4)
    xy0=pdict_m2m3[itisar.name]['CLKCAL0<0>'][0]
    xy1=pdict_m2m3[itisar.name]['CLKCAL'+str(num_slices-1)+'<3>'][0]
    rclk_m2m3=[]
    for i in range(num_slices):
        rclk_m2m3.append([])
        for j in range(5):
            rh0, rv0 = laygen.route_hv(laygen.layers['metal'][2], laygen.layers['metal'][3],
                            xy0=pdict_m2m3[itisar.name]['CLKCAL'+str(i)+'<'+str(j)+'>'][0],
                            xy1=xy1-np.array([10*i+2*j,-4]),
                            gridname0=rg_m2m3)
            rclk_m2m3[i].append(rv0)
    for i in range(num_slices):
        for j in range(5):
            xy0=laygen.get_rect_xy(rclk_m2m3[i][j].name, gridname=rg_m3m4, sort=True)[1]
            #xy0=laygen.get_rect_xy(rclk_m3m4[i][j].name, gridname=rg_m3m4, sort=True)[1]
            rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                            xy0=xy0,
                            xy1=pdict_m3m4[iclkgbuf.name]['CLKCAL'+str(i)+'<'+str(j)+'>'][0],
                            track_y=xy0[1]-10*i-2*j+40,
                            gridname0=rg_m3m4)
    for i in range(num_slices):
        for j in range(5):
            xy0=pdict_m3m4[iclkgbuf.name]['clkgcal'+str(i)+'<'+str(j)+'>'][0]
            r=laygen.route(None, layer=laygen.layers['metal'][3], xy0=xy0, xy1=np.array([xy0[0], 0]), gridname0=rg_m3m4)
            laygen.boundary_pin_from_rect(r, rg_m3m4, 'clkgcal'+str(i)+'<'+str(j)+'>', laygen.layers['pin'][3], size=6, direction='bottom')
    '''
    rclk_m3m4=[]
    for i in range(num_slices):
        rclk_m3m4.append([])
        for j in range(5):
            xy0=laygen.get_rect_xy(rclk_m2m3[i][j].name, gridname=rg_m3m4, sort=True)[1]
            rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4],
                            xy0=xy0,
                            xy1=xy0+np.array([10*num_slices+32, -10*i-2*j+40]),
                            gridname0=rg_m3m4)
            rclk_m3m4[i].append(rh0)
    for i in range(num_slices):
        for j in range(5):
            xy0=laygen.get_rect_xy(rclk_m3m4[i][j].name, gridname=rg_m3m4, sort=True)[1]
            r=laygen.route(None, layer=laygen.layers['metal'][3], xy0=xy0, xy1=np.array([xy0[0], 0]), gridname0=rg_m3m4, addvia0=True)
            laygen.boundary_pin_from_rect(r, rg_m3m4, 'clkgcal'+str(i)+'<'+str(j)+'>', laygen.layers['pin'][3], size=6, direction='bottom')
    '''

    #other pins - duplicate
    pin_prefix_list=['RSTP', 'RSTN', 'CLKIP', 'CLKIN', 'VREF']
    for pn, p in tisar_pins.items():
        for pfix in pin_prefix_list:
            if pn.startswith(pfix):
                laygen.add_pin(pn, tisar_pins[pn]['netname'], tisar_xy+tisar_pins[pn]['xy'], tisar_pins[pn]['layer'])


    '''
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
    laygen.add_pin('ADCBIAS', 'ADCBIAS', sf_xy+sf_pins['ADCBIAS0']['xy'], sf_pins['ADCBIAS0']['layer'])
    #pins - vrefin, osp, osm
    pinmap_out=[None, None, None]
    pinmap_out+=['VOSP'+str(num_slice-1-j) for j in range(num_slice)]
    pinmap_out+=['VOSM'+str(num_slice-1-j) for j in range(num_slice)]
    pinmap_out+=['VDUM0']
    pdict = laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    xy0=pdict[isf.name]['VREF1<'+str(num_bias-1)+'>'][0]+np.array([4,0])
    for i in range(num_rdac):
        for j in range(5):
            if i==0 and j<3:
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5], pdict[irdac.name]['out0<'+str(4-j)+'>'][0], pdict[isf.name]['VIN0<'+str(2-j)+'>'][0], gridname=rg_m5m6_thick)
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5], pdict[irdac.name]['out0<'+str(4-j)+'>'][0], pdict[isf.name]['VIN1<'+str(2-j)+'>'][0], gridname=rg_m5m6_thick)
            else:
                if not pinmap_out[i*5+j].startswith('VDUM'):
                    rh0, rv0 = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5], pdict[irdac.name]['out'+str(i)+'<'+str(4-j)+'>'][0], xy0, gridname=rg_m5m6_thick)
                    xy0=xy0+np.array([1,0])
                    laygen.boundary_pin_from_rect(rv0, rg_m5m6_thick, pinmap_out[i*5+j], laygen.layers['pin'][5], size=6, direction='bottom')
    #pins - VREF
    for i in range(num_bias):
        laygen.add_pin('VREF0<'+str(i)+'>', 'VREF<'+str(i)+'>', sf_xy+sf_pins['VREF0<'+str(i)+'>']['xy'], sf_pins['VREF0<'+str(i)+'>']['layer'])
        laygen.add_pin('VREF1<'+str(i)+'>', 'VREF<'+str(i)+'>', sf_xy+sf_pins['VREF1<'+str(i)+'>']['xy'], sf_pins['VREF1<'+str(i)+'>']['layer'])
    '''        

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
    rg_m2m3_basic = 'route_M2_M3_basic'
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

    cellname = 'tisaradc_top'
    tisar_name = 'tisaradc_body'
    bias_name = 'sarbias_top_'+str(num_slices)+'slice'

    #generation
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_tisaradc_top(laygen, objectname_pfix='TISAR0', tisar_libname=workinglib, bias_libname=workinglib,
                          tisar_name=tisar_name, bias_name=bias_name, 
                          placement_grid=pg,
                          routing_grid_m2m3 = rg_m2m3_basic,
                          routing_grid_m3m4 = rg_m3m4,
                          routing_grid_m4m5 = rg_m4m5,
                          routing_grid_m5m6_thick=rg_m5m6_thick, 
                          num_slice=num_slices, origin=np.array([0, 0]))
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
