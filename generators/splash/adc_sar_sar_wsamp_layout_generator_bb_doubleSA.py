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

def generate_sar_wsamp(laygen, objectname_pfix, workinglib, samp_lib, space_1x_lib, sar_name, samp_name, space_1x_name,
                       placement_grid, routing_grid_m5m6, routing_grid_m3m4_basic_thick,
                       routing_grid_m5m6_thick, routing_grid_m5m6_thick_basic,
                       num_inv_bb=0, num_bits=9, use_sf=False, vref_sf=False, origin=np.array([0, 0])):
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

    # source follower
    sf_name = 'sourceFollower_diff'
    if use_sf == True:
        isf = laygen.relplace(name="I" + objectname_pfix + 'SF0', templatename=sf_name,
                                gridname=pg, refinstname=isamp.name, direction='top', template_libname=workinglib)
        sf_xy=isf.xy

    #prboundary
    sar_size = laygen.templates.get_template(sar_name, libname=workinglib).size
    samp_size = laygen.templates.get_template(samp_name, libname=samp_lib).size
    sf_size = laygen.templates.get_template(sf_name, libname=workinglib).size
    space_size = laygen.templates.get_template(space_1x_name, libname=space_1x_lib).size
    size_x=sar_size[0]
    size_y=int((sar_size[1]+samp_size[1])/space_size[1]+1)*space_size[1]
    if use_sf == True:
        size_y = int((sar_size[1] + samp_size[1] + sf_size[1]) / space_size[1] + 1) * space_size[1]
    laygen.add_rect(None, np.array([origin, origin+np.array([size_x, size_y])]), laygen.layers['prbnd'])

    # template handles
    sar_template = laygen.templates.get_template(sar_name, workinglib)
    samp_template = laygen.templates.get_template(samp_name, samp_lib)
    sf_template = laygen.templates.get_template(sf_name, workinglib)

    #reference coordinates
    pdict_m5m6=laygen.get_inst_pin_xy(None, None, rg_m5m6)
    pdict_m5m6_thick=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    pdict_m5m6_thick_basic=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick_basic)
    sar_pins=sar_template.pins
    samp_pins=samp_template.pins
    sf_pins=sf_template.pins
    #sar_xy=isar.xy[0]
    #samp_xy=isamp.xy[0]
    sar_xy=isar.xy
    samp_xy=isamp.xy

    #signal route (clk/inp/inm)
    #make virtual grids and route on the grids (assuming drc clearance of each block)
    rg_m5m6_thick_basic_temp_sig='route_M5_M6_thick_basic_temp_sig'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m5m6_thick_basic, gridname_output=rg_m5m6_thick_basic_temp_sig,
                                          instname=isamp.name, 
                                          inst_pin_prefix=['ckout'], xy_grid_type='xgrid')
    pdict_m5m6_thick_basic_temp_sig = laygen.get_inst_pin_xy(None, None, rg_m5m6_thick_basic_temp_sig)
    rg_m4m5_basic_thick_temp_sig='route_M4_M5_basic_thick_temp_sig'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m4m5_basic_thick, gridname_output=rg_m4m5_basic_thick_temp_sig,
                                          instname=isamp.name, 
                                          inst_pin_prefix=['outp', 'outn'], xy_grid_type='xgrid')
    pdict_m4m5_basic_thick_temp_sig = laygen.get_inst_pin_xy(None, None, rg_m4m5_basic_thick_temp_sig)
    #clock
    rclk0 = laygen.route(None, laygen.layers['metal'][5],
                         xy0=pdict_m5m6_thick_basic_temp_sig[isamp.name]['ckout'][0],
                         xy1=pdict_m5m6_thick_basic_temp_sig[isar.name]['CLK0'][1]-np.array([0,1]), gridname0=rg_m5m6_thick_basic_temp_sig)
    laygen.via(None,pdict_m5m6_thick_basic_temp_sig[isar.name]['CLK0'][1], rg_m5m6_thick_basic_temp_sig)
    laygen.via(None,pdict_m5m6_thick_basic_temp_sig[isar.name]['CLK1'][1], rg_m5m6_thick_basic_temp_sig)
    #laygen.via(None,pdict_m5m6_thick_basic_temp_sig[isar.name]['CLK2'][1], rg_m5m6_thick_basic_temp_sig)
    #rclk0 = laygen.route(None, laygen.layers['metal'][5],
    #                     xy0=pdict_m5m6_thick_basic[isamp.name]['ckout'][0],
    #                     xy1=pdict_m5m6_thick_basic[isar.name]['CLK'][1]-np.array([0,1]), gridname0=rg_m5m6_thick_basic)
    #laygen.via(None,pdict_m5m6_thick_basic[isar.name]['CLK'][1], rg_m5m6_thick_basic)

    #frontend sig
    inp_y_list=[]
    inm_y_list=[]
    for pn, p in pdict_m4m5_basic_thick_temp_sig[isar.name].items():
        if pn.startswith('INP'):
            inp_y_list.append(p[0][1])
            pv=np.array([pdict_m4m5_basic_thick_temp_sig[isamp.name]['outp'][0][0], p[0][1]])
            laygen.via(None,pv, rg_m4m5_basic_thick_temp_sig)
            #laygen.via(None,p[0], rg_m5m6_thick_basic_temp_sig)
        if pn.startswith('INM'):
            inm_y_list.append(p[0][1])
            pv=np.array([pdict_m4m5_basic_thick_temp_sig[isamp.name]['outn'][0][0], p[0][1]])
            laygen.via(None,pv, rg_m4m5_basic_thick_temp_sig)
            #laygen.via(None,p[0], rg_m5m6_thick_basic_temp_sig)
    inp_y=min(inp_y_list)
    inm_y=min(inm_y_list)
    rinp0 = laygen.route(None, laygen.layers['metal'][5],
                         xy0=pdict_m4m5_basic_thick_temp_sig[isamp.name]['outp'][0],
                         xy1=np.array([pdict_m4m5_basic_thick_temp_sig[isamp.name]['outp'][0][0],inp_y-1]), 
                         gridname0=rg_m4m5_basic_thick_temp_sig)
    rinm0 = laygen.route(None, laygen.layers['metal'][5],
                         xy0=pdict_m4m5_basic_thick_temp_sig[isamp.name]['outn'][0],
                         xy1=np.array([pdict_m4m5_basic_thick_temp_sig[isamp.name]['outn'][0][0],inm_y-1]), 
                         gridname0=rg_m4m5_basic_thick_temp_sig)
    #rinp0 = laygen.route(None, laygen.layers['metal'][5],
    #                     xy0=pdict_m5m6_thick_basic_temp_sig[isamp.name]['outp'][0],
    #                     xy1=np.array([pdict_m5m6_thick_basic_temp_sig[isar.name]['INP0'][0][0],inp_y-1]), 
    #                     gridname0=rg_m5m6_thick_basic_temp_sig)
    #rinm0 = laygen.route(None, laygen.layers['metal'][5],
    #                     xy0=pdict_m5m6_thick_basic_temp_sig[isamp.name]['outn'][0],
    #                     xy1=np.array([pdict_m5m6_thick_basic_temp_sig[isar.name]['INM0'][0][0],inm_y-1]), 
    #                     gridname0=rg_m5m6_thick_basic_temp_sig)

    # source follower routing
    pdict_m4m5_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_thick)
    if use_sf == True:
        [rh0, rv0] = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5_thick[isf.name]['outp'][0],
                                     pdict_m4m5_thick[isamp.name]['inp'][0], rg_m4m5_thick)
        [rh0, rv0] = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5], pdict_m4m5_thick[isf.name]['outn'][0],
                                     pdict_m4m5_thick[isamp.name]['inn'][0], rg_m4m5_thick)
        # VDD/VSS for source follower
        for pn, p in samp_pins.items():
            if pn.startswith('LVDD'):
                laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][4],
                                pdict_m4m5_thick[isamp.name][pn][0], pdict_m4m5_thick[isf.name]['VDD0'][0], rg_m4m5_thick)
                laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][4],
                            pdict_m4m5_thick[isamp.name][pn][0], pdict_m4m5_thick[isf.name]['VDD1'][0], rg_m4m5_thick)
            if pn.startswith('RVDD'):
                laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][4],
                                pdict_m4m5_thick[isamp.name][pn][0], pdict_m4m5_thick[isf.name]['VDD0'][0], rg_m4m5_thick)
                laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][4],
                            pdict_m4m5_thick[isamp.name][pn][0], pdict_m4m5_thick[isf.name]['VDD1'][0], rg_m4m5_thick)
            if pn.startswith('LVSS'):
                laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][4],
                                pdict_m4m5_thick[isamp.name][pn][0], pdict_m4m5_thick[isf.name]['VSS0'][0], rg_m4m5_thick)
                laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][4],
                            pdict_m4m5_thick[isamp.name][pn][0], pdict_m4m5_thick[isf.name]['VSS1'][0], rg_m4m5_thick)
            if pn.startswith('RVSS'):
                laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][4],
                                pdict_m4m5_thick[isamp.name][pn][0], pdict_m4m5_thick[isf.name]['VSS0'][0], rg_m4m5_thick)
                laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][4],
                            pdict_m4m5_thick[isamp.name][pn][0], pdict_m4m5_thick[isf.name]['VSS1'][0], rg_m4m5_thick)

    #input pins (just duplicate from lower hierarchy cells)
    laygen.add_pin('CLK', 'CLK', samp_xy+samp_pins['ckin']['xy'], samp_pins['ckin']['layer'])
    if use_sf == False:
        laygen.add_pin('INP', 'INP', samp_xy+samp_pins['inp']['xy'], samp_pins['inp']['layer'])
        laygen.add_pin('INM', 'INM', samp_xy+samp_pins['inn']['xy'], samp_pins['inn']['layer'])
    else:
        laygen.add_pin('INP', 'INP', sf_xy+sf_pins['inp']['xy'], sf_pins['inp']['layer'])
        laygen.add_pin('INM', 'INM', sf_xy+sf_pins['inn']['xy'], sf_pins['inn']['layer'])
        for pn, p in sf_pins.items():
            if pn.startswith('Voffp'):
                pxy = sf_xy + sf_pins[pn]['xy']
                laygen.add_pin('SF_'+pn, 'SF_Voffp', pxy, sf_pins[pn]['layer'])
            if pn.startswith('Voffn'):
                pxy = sf_xy + sf_pins[pn]['xy']
                laygen.add_pin('SF_'+pn, 'SF_Voffn', pxy, sf_pins[pn]['layer'])
            if pn.startswith('bypass'):
                pxy = sf_xy + sf_pins[pn]['xy']
                laygen.add_pin('SF_'+pn, 'SF_bypass', pxy, sf_pins[pn]['layer'])
            if pn.startswith('VBIAS'):
                pxy = sf_xy + sf_pins[pn]['xy']
                laygen.add_pin('SF_BIAS', 'SF_BIAS', pxy, sf_pins[pn]['layer'])
            # if pn.startswith('VBIASn'):
            #     pxy = sf_xy + sf_pins[pn]['xy']
            #     laygen.add_pin('SF_BIASn', 'SF_BIASn', pxy, sf_pins[pn]['layer'])

    if vref_sf == True:
        laygen.add_pin('VREF_SF_BIAS', 'VREF_SF_BIAS', sar_xy+sar_pins['SF_VBIAS']['xy'], sar_pins['SF_VBIAS']['layer'])
        laygen.add_pin('VREF_SF_bypass', 'VREF_SF_bypass', sar_xy+sar_pins['SF_bypass']['xy'], sar_pins['SF_bypass']['layer'])

    laygen.add_pin('OSP', 'OSP', sar_xy+sar_pins['OSP']['xy'], sar_pins['OSP']['layer'])
    laygen.add_pin('OSM', 'OSM', sar_xy+sar_pins['OSM']['xy'], sar_pins['OSM']['layer'])
    for pn, p in sar_pins.items():
        if pn.startswith('VREF<0>'):
            pxy=sar_xy+sar_pins[pn]['xy']
            laygen.add_pin(pn, 'VREF<0>', pxy, sar_pins[pn]['layer'])
        if pn.startswith('VREF<1>'):
            pxy=sar_xy+sar_pins[pn]['xy']
            laygen.add_pin(pn, 'VREF<1>', pxy, sar_pins[pn]['layer'])
        if pn.startswith('VREF<2>'):
            pxy=sar_xy+sar_pins[pn]['xy']
            laygen.add_pin(pn, 'VREF<2>', pxy, sar_pins[pn]['layer'])
    #laygen.add_pin('VREF_M5R<2>', 'VREF<2>', sar_xy+sar_pins['VREF_M5R<2>']['xy'], sar_pins['VREF_M5R<2>']['layer'])
    #laygen.add_pin('VREF_M5R<1>', 'VREF<1>', sar_xy+sar_pins['VREF_M5R<1>']['xy'], sar_pins['VREF_M5R<1>']['layer'])
    #laygen.add_pin('VREF_M5R<0>', 'VREF<0>', sar_xy+sar_pins['VREF_M5R<0>']['xy'], sar_pins['VREF_M5R<0>']['layer'])
    #laygen.add_pin('VREF_M5L<2>', 'VREF<2>', sar_xy+sar_pins['VREF_M5L<2>']['xy'], sar_pins['VREF_M5L<2>']['layer'])
    #laygen.add_pin('VREF_M5L<1>', 'VREF<1>', sar_xy+sar_pins['VREF_M5L<1>']['xy'], sar_pins['VREF_M5L<1>']['layer'])
    #laygen.add_pin('VREF_M5L<0>', 'VREF<0>', sar_xy+sar_pins['VREF_M5L<0>']['xy'], sar_pins['VREF_M5L<0>']['layer'])
    laygen.add_pin('CKDSEL0<1>', 'CKDSEL0<1>', sar_xy+sar_pins['CKDSEL0<1>']['xy'], sar_pins['CKDSEL0<1>']['layer'])
    laygen.add_pin('CKDSEL0<0>', 'CKDSEL0<0>', sar_xy+sar_pins['CKDSEL0<0>']['xy'], sar_pins['CKDSEL0<0>']['layer'])
    laygen.add_pin('CKDSEL1<1>', 'CKDSEL1<1>', sar_xy+sar_pins['CKDSEL1<1>']['xy'], sar_pins['CKDSEL1<1>']['layer'])
    laygen.add_pin('CKDSEL1<0>', 'CKDSEL1<0>', sar_xy+sar_pins['CKDSEL1<0>']['xy'], sar_pins['CKDSEL1<0>']['layer'])
    #laygen.add_pin('EXTCLK', 'EXTCLK', sar_xy+sar_pins['EXTCLK']['xy'], sar_pins['EXTCLK']['layer'])
    laygen.add_pin('EXTSEL_CLK', 'EXTSEL_CLK', sar_xy+sar_pins['EXTSEL_CLK']['xy'], sar_pins['EXTSEL_CLK']['layer'])
    #output pins (just duplicate from lower hierarchy cells)
    for i in range(num_bits):
        pn='ADCOUT'+'<'+str(i)+'>'
        laygen.add_pin(pn, pn, sar_xy+sar_pins[pn]['xy'], sar_pins[pn]['layer'])
    laygen.add_pin('CLKO0', 'CLKO', sar_xy+sar_pins['CLKOUT0']['xy'], sar_pins['CLKOUT0']['layer'])
    laygen.add_pin('CLKO1', 'CLKO', sar_xy+sar_pins['CLKOUT1']['xy'], sar_pins['CLKOUT1']['layer'])
    #laygen.add_pin('CLKO2', 'CLKO', sar_xy+sar_pins['CLKOUT2']['xy'], sar_pins['CLKOUT2']['layer'])
    
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

    #VDD/VSS pin
    vddcnt=0
    vsscnt=0
    for p in pdict_m5m6[isar.name]:
        if p.startswith('VDD'):
            xy0=pdict_m5m6_thick[isar.name][p]
            laygen.pin(name='VDDSAR' + str(vddcnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VDDSAR')
            vddcnt+=1
        if p.startswith('VSS'):
            xy0=pdict_m5m6_thick[isar.name][p]
            laygen.pin(name='VSSSAR' + str(vsscnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VSS:')
            #laygen.pin(name='VSSSAR' + str(vsscnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick, netname='VSS')
            vsscnt+=1
    #extract VDD/VSS grid from samp and make power pins
    rg_m5m6_thick_temp_samp='route_M5_M6_thick_temp_samp'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_samp,
                                          instname=isamp.name, 
                                          inst_pin_prefix=['VDD', 'VSS', 'samp_body'], xy_grid_type='ygrid')
    pdict_m5m6_thick_temp_samp = laygen.get_inst_pin_xy(None, None, rg_m5m6_thick_temp_samp)
    vddcnt=0
    vsscnt=0
    bodycnt=0
    for p in pdict_m5m6_thick_temp_samp[isamp.name]:
        if p.startswith('VDD'):
            xy0=pdict_m5m6_thick_temp_samp[isamp.name][p]
            laygen.pin(name='VDDSAMP' + str(vddcnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick_temp_samp, netname='VDDSAMP')
            vddcnt+=1
        if p.startswith('VSS'):
            xy0=pdict_m5m6_thick_temp_samp[isamp.name][p]
            laygen.pin(name='VSSSAMP' + str(vsscnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick_temp_samp, netname='VSS:')
            #laygen.pin(name='VSSSAMP' + str(vsscnt), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick_temp_samp, netname='VSS')
            vsscnt+=1
        if p.startswith('samp_body'):
            xy0=pdict_m5m6_thick_temp_samp[isamp.name][p]
            laygen.pin(name='samp_body', layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick_temp_samp, netname='samp_body')
            bodycnt+=1
    # VBB
    pdict_m3m4 = laygen.get_inst_pin_xy(None, None, rg_m3m4_basic_thick)
    if not num_inv_bb==0:
        rvbb_m3=[]
        for p in pdict_m3m4[isar.name]:
            if p.startswith('VBB') and p.endswith('0'):
                rvbb_m3.append(pdict_m3m4[isar.name][p])
                # laygen.pin(name='bottom_body'+str(p), layer=laygen.layers['pin'][3], xy=pdict_m3m4[isar.name][p], gridname=rg_m3m4, netname='bottom_body')
        rvbb_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_M4_',
                                                                    layer=laygen.layers['metal'][4],
                                                                    gridname=rg_m3m4_basic_thick, netnames=['bottom_body'],
                                                                    direction='x',
                                                                    input_rails_xy=[rvbb_m3],
                                                                    generate_pin=False, overwrite_start_coord=None,
                                                                    overwrite_end_coord=None,
                                                                    offset_start_index=0, offset_end_index=0)
        rvbb_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M5_',
                                                                    layer=laygen.layers['metal'][5],
                                                                    gridname=rg_m4m5_thick, netnames=['bottom_body'],
                                                                    direction='y',
                                                                    input_rails_rect=rvbb_m4,
                                                                    generate_pin=False, overwrite_start_coord=None,
                                                                    overwrite_end_coord=None,
                                                                    offset_start_index=0, offset_end_index=-2)
        rvbb_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_',
                                                                    layer=laygen.layers['metal'][6],
                                                                    gridname=rg_m5m6_thick, netnames=['bottom_body'],
                                                                    direction='x',
                                                                    input_rails_rect=rvbb_m5,
                                                                    generate_pin=False, overwrite_start_coord=None,
                                                                    overwrite_end_coord=None,
                                                                    offset_start_index=0, offset_end_index=0)
        num_m6 = len(rvbb_m6[0])
        for i in range(num_m6):
            if i%2==1:
                rvbb_m6[0].remove(rvbb_m6[0][num_m6-i-1])
            print(rvbb_m6[0])
        rvbb_m7 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M7_',
                                                                    layer=laygen.layers['pin'][7],
                                                                    gridname=rg_m6m7_thick, netnames=['bottom_body'],
                                                                    direction='y',
                                                                    input_rails_rect=rvbb_m6,
                                                                    generate_pin=True, overwrite_start_coord=None,
                                                                    overwrite_end_coord=None,
                                                                    offset_start_index=0, offset_end_index=0)
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
    rg_m3m4_basic_thick = 'route_M3_M4_basic_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_basic_thick = 'route_M4_M5_basic_thick'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m5m6_basic_thick = 'route_M5_M6_basic_thick'
    rg_m5m6_thick_basic = 'route_M5_M6_thick_basic'
    rg_m6m7_thick = 'route_M6_M7_thick'
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
        use_sf=specdict['use_sf']
        vref_sf=specdict['use_vref_sf']
        num_inv_bb=sizedict['sarlogic']['num_inv_bb']
        if specdict['samp_use_laygo'] is True:
            samp_lib = 'adc_sar_generated'
            samp_name = 'sarsamp_bb'
        else:
            laygen.load_template(filename=samp_lib+'.yaml', libname=samp_lib)
    #yamlfile_system_input="adc_sar_dsn_system_input.yaml"
    #if load_from_file==True:
    #    with open(yamlfile_system_input, 'r') as stream:
    #        sysdict_i = yaml.load(stream)
    #    num_bits=sysdict_i['n_bit']
    #sar generation
    cellname='sar_wsamp_bb_doubleSA' #_'+str(num_bits)+'b'
    sar_name = 'sar_doubleSA_bb' #_'+str(num_bits)+'b'
    space_1x_name = 'space_1x'

    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sar_wsamp(laygen, objectname_pfix='SA0', workinglib=workinglib, samp_lib=samp_lib, space_1x_lib=logictemplib,
                       sar_name=sar_name, samp_name=samp_name, space_1x_name=space_1x_name,
                       placement_grid=pg, routing_grid_m5m6=rg_m5m6, routing_grid_m5m6_thick=rg_m5m6_thick,
                       routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic, routing_grid_m3m4_basic_thick=rg_m3m4_basic_thick,
                       num_inv_bb=num_inv_bb, num_bits=num_bits, use_sf=use_sf, vref_sf=vref_sf, origin=np.array([0, 0]))
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
