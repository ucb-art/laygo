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
import os
import yaml
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_source_follower_diff(laygen, objectname_pfix, placement_grid, routing_grid_m1m2, devname_mos_boundary, devname_mos_body,
                             devname_mos_dmy, devname_tap_boundary, devname_tap_body,
                             devname_mos_space_4x, devname_mos_space_2x, devname_mos_space_1x,
                             devname_tap_space_4x, devname_tap_space_2x, devname_tap_space_1x,
                             m_mir=2, m_bias=2, m_in=2, m_ofst=2, m_bias_dum=2, m_in_dum=2, m_byp=2, m_byp_bias=2, origin=np.array([0,0])):
    """generate an analog differential mos structure with dummmies """
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    # placement
    # generate boundary
    x_off = laygen.get_template_size('sourceFollower', gridname=pg, libname=workinglib)[0]
    isfl = laygen.relplace("I" + objectname_pfix + 'SFL', 'sourceFollower', pg, xy=origin+np.array([x_off, 0]), transform='MY', template_libname=workinglib)
    isfr = laygen.relplace("I" + objectname_pfix + 'SFR', 'sourceFollower', pg, isfl.name, direction='right', transform='R0', template_libname=workinglib)
    isf_list = [isfl, isfr]
    isf_suffix_list = ['p','n']

    # pins
    sf_template = laygen.templates.get_template('sourceFollower', workinglib)
    sf_pins=sf_template.pins
    sfl_xy=isfl.xy
    sfr_xy=isfr.xy
    pdict_m3m4=laygen.get_inst_pin_xy(None, None, rg_m3m4)
    pdict_m3m4_thick=laygen.get_inst_pin_xy(None, None, rg_m3m4_basic_thick)
    pdict_m4m5_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_thick)

    outcnt = [0, 0]
    incnt = [0, 0]
    vbiascnt = [0, 0]
    voffcnt = [0, 0]
    for pn, p in sf_pins.items():
        # output pins
        if pn.startswith('out'):
            for i in range(len(isf_list)):
                # pn='out'
                pn_out='out'+isf_suffix_list[i]
                laygen.pin(name=pn_out, layer=sf_pins[pn]['layer'], netname='out'+isf_suffix_list[i],
                           xy=pdict_m3m4_thick[isf_list[i].name][pn], gridname=rg_m3m4_basic_thick)
                outcnt[i]+=1
    # # input pins
    # for pn, p in sf_pins.items():
    #     if pn.startswith('in'):
    #         for i in range(len(isf_list)):
    #             pn_out = 'in' + isf_suffix_list[i] + str(incnt[i])
    #             laygen.pin(name=pn_out, layer=sf_pins[pn]['layer'], netname='in' + isf_suffix_list[i],
    #                        xy=pdict_m3m4[isf_list[i].name][pn], gridname=rg_m3m4)
    #             incnt[i] += 1
    pn = 'in'
    for i in range(len(isf_list)):
        pn_out = 'in' + isf_suffix_list[i]
        laygen.pin(name=pn_out, layer=sf_pins[pn]['layer'], netname='in' + isf_suffix_list[i],
                   xy=pdict_m4m5_thick[isf_list[i].name][pn], gridname=rg_m4m5_thick)
    # vbias pins
    rvb_list = []
    for i in range(len(isf_list)):
        vbias_xy = []
        for pn, p in sf_pins.items():
            if pn.startswith('VBIAS'):
                vbias_xy.append(pdict_m3m4_thick[isf_list[i].name][pn][0])
                # laygen.pin(name=pn_out, layer=sf_pins[pn]['layer'], netname='VBIAS' + isf_suffix_list[i],
                #            xy=pdict_m3m4[isf_list[i].name][pn], gridname=rg_m3m4)
                # vbiascnt[i] += 1
        for j in range(len(vbias_xy)-1):
            laygen.route(None, laygen.layers['metal'][4], xy0=vbias_xy[j], xy1=vbias_xy[j+1], gridname0=rg_m3m4_basic_thick,
                         via0=[0, 0], via1=[0, 0])
        rvb = laygen.route(None, laygen.layers['metal'][5], xy0=pdict_m4m5_thick[isf_list[i].name]['VBIAS0'][0],
                     xy1=pdict_m4m5_thick[isf_list[i].name]['VBIAS0'][0]+np.array([0, 4]),
                     gridname0=rg_m4m5_thick, via0=[0, 0])
        rvb_list.append(rvb)
        rh0 = laygen.route(None, laygen.layers['metal'][4], xy0=pdict_m3m4_thick[isf_list[i].name]['Voff'][0]+np.array([0, 1]),
                     xy1=pdict_m3m4_thick[isf_list[i].name]['Voff'][0]+np.array([3*(-1)**i, 1]),
                     gridname0=rg_m3m4_basic_thick, via0=[0, 0])
        rvoff = laygen.route(None, laygen.layers['metal'][5], xy0=pdict_m4m5_thick[isf_list[i].name]['Voff'][0]+np.array([0, 0]),
                     xy1=pdict_m4m5_thick[isf_list[i].name]['Voff'][0]+np.array([0, 4]),
                     gridname0=rg_m4m5_thick, via0=[0, 1])
        # pn_out = 'VBIAS' + isf_suffix_list[i]
        # laygen.boundary_pin_from_rect(rvb, rg_m4m5_thick, pn_out, laygen.layers['pin'][5], size=4, direction='top')
        pn_out = 'Voff' + isf_suffix_list[i]
        laygen.boundary_pin_from_rect(rvoff, rg_m4m5_thick, pn_out, laygen.layers['pin'][5], size=4, direction='top')
    rvb = laygen.route(None, laygen.layers['metal'][6], xy0=laygen.get_rect_xy(rvb_list[0].name, rg_m5m6_thick)[0],
                       xy1=laygen.get_rect_xy(rvb_list[1].name, rg_m5m6_thick)[0],
                       gridname0=rg_m5m6_thick, via0=[0, 0], via1=[0, 0])
    laygen.pin_from_rect('VBIAS', laygen.layers['pin'][6], rvb, rg_m5m6_thick)

    # for pn, p in sf_pins.items():
    #     if pn.startswith('VBIAS'):
    #         for i in range(len(isf_list)):
    #             pn_out = 'VBIAS' + isf_suffix_list[i] + str(vbiascnt[i])
    #             laygen.pin(name=pn_out, layer=sf_pins[pn]['layer'], netname='VBIAS' + isf_suffix_list[i],
    #                        xy=pdict_m3m4[isf_list[i].name][pn], gridname=rg_m3m4)
    #             vbiascnt[i] += 1
    # pn = 'VBIAS'
    # for i in range(len(isf_list)):
    #     pn_out = 'VBIAS' + isf_suffix_list[i] + str(incnt[i])
    #     laygen.pin(name=pn_out, layer=sf_pins[pn]['layer'], netname='VBIAS' + isf_suffix_list[i],
    #                xy=pdict_m3m4[isf_list[i].name][pn], gridname=rg_m3m4)

    # # voff pins
    # for pn, p in sf_pins.items():
    #     if pn.startswith('Voff'):
    #         for i in range(len(isf_list)):
    #             pn_out = 'Voff' + isf_suffix_list[i] + str(voffcnt[i])
    #             laygen.pin(name=pn_out, layer=sf_pins[pn]['layer'], netname='Voff' + isf_suffix_list[i],
    #                        xy=pdict_m3m4[isf_list[i].name][pn], gridname=rg_m3m4)
    #             voffcnt[i] += 1
    # pn = 'Voff'
    # for i in range(len(isf_list)):
    #     pn_out = 'Voff' + isf_suffix_list[i] + str(incnt[i])
    #     laygen.pin(name=pn_out, layer=sf_pins[pn]['layer'], netname='Voff' + isf_suffix_list[i],
    #                xy=pdict_m3m4[isf_list[i].name][pn], gridname=rg_m3m4)

    # #VDD/VSS pins
    # vddcnt=0
    # vsscnt=0
    # for pn, p in sf_pins.items():
    #     if pn.startswith('VDD'):
    #         pxyl=sfl_xy+sf_pins[pn]['xy']
    #         laygen.add_pin('VDDL' + str(vddcnt), 'VDD:', pxyl, sf_pins[pn]['layer'])
    #         pxyr=sfr_xy+sf_pins[pn]['xy']
    #         laygen.add_pin('VDDR' + str(vddcnt), 'VDD:', pxyr, sf_pins[pn]['layer'])
    #         vddcnt+=1
    #     if pn.startswith('VSS'):
    #         pxyl=sfl_xy+sf_pins[pn]['xy']
    #         laygen.add_pin('VSSL' + str(vsscnt), 'VSS:', pxyl, sf_pins[pn]['layer'])
    #         pxyr=sfr_xy+sf_pins[pn]['xy']
    #         laygen.add_pin('VSSR' + str(vsscnt), 'VSS:', pxyr, sf_pins[pn]['layer'])
    #         vsscnt+=1

    # bypass route
    rbyp = laygen.route(None, layer=laygen.layers['metal'][4], xy0=pdict_m3m4[isfl.name]['bypass'][0],
                     xy1=pdict_m3m4[isfr.name]['bypass'][0], gridname0=rg_m3m4, via0=[0,0], via1=[0,0])
    print(laygen.get_xy(rbyp, rg_m3m4))
    laygen.pin(name='bypass', layer=laygen.layers['pin'][4], xy=laygen.get_xy(rbyp, rg_m3m4), gridname=rg_m3m4)

    # M4 VSS/VDD lower rails
    pdict_m3m4_bt=laygen.get_inst_pin_xy(None, None, rg_m3m4_basic_thick)
    ref_y = pdict_m3m4_bt[isfl.name]['VSS0'][0][1]
    x0 = laygen.get_template_size('sourceFollower', rg_m3m4_basic_thick, libname=workinglib)[0]*2
    rvss0 = laygen.route(None, laygen.layers['metal'][4], xy0=[0, ref_y], xy1=[x0, ref_y], gridname0=rg_m3m4_basic_thick)
    rvdd0 = laygen.route(None, laygen.layers['metal'][4], xy0=[0, ref_y+1], xy1=[x0, ref_y+1], gridname0=rg_m3m4_basic_thick)
    laygen.pin(name='VSS0', layer=laygen.layers['pin'][4], xy=laygen.get_xy(rvss0, rg_m3m4_basic_thick),
               netname='VSS', gridname=rg_m3m4_basic_thick)
    laygen.pin(name='VDD0', layer=laygen.layers['pin'][4], xy=laygen.get_xy(rvdd0, rg_m3m4_basic_thick),
               netname='VDD', gridname=rg_m3m4_basic_thick)
    for pn, p in sf_pins.items():
        if pn.startswith('VSS'):
            pxyl=pdict_m3m4_bt[isfl.name][pn]
            pxyr=pdict_m3m4_bt[isfr.name][pn]
            laygen.via(None, np.array([pxyl[0][0], ref_y]), gridname=rg_m3m4_basic_thick)
            laygen.via(None, np.array([pxyr[0][0], ref_y]), gridname=rg_m3m4_basic_thick)
        if pn.startswith('VDD'):
            pxyl=pdict_m3m4_bt[isfl.name][pn]
            pxyr=pdict_m3m4_bt[isfr.name][pn]
            laygen.via(None, np.array([pxyl[0][0], ref_y+1]), gridname=rg_m3m4_basic_thick)
            laygen.via(None, np.array([pxyr[0][0], ref_y+1]), gridname=rg_m3m4_basic_thick)

    # M4 VSS/VDD upper rails
    ref_y = pdict_m3m4_bt[isfl.name]['VSS0'][1][1]
    rvss1 = laygen.route(None, laygen.layers['metal'][4], xy0=[0, ref_y-1], xy1=[x0, ref_y-1], gridname0=rg_m3m4_basic_thick)
    rvdd1 = laygen.route(None, laygen.layers['metal'][4], xy0=[0, ref_y], xy1=[x0, ref_y], gridname0=rg_m3m4_basic_thick)
    laygen.pin(name='VSS1', layer=laygen.layers['pin'][4], xy=laygen.get_xy(rvss1, rg_m3m4_basic_thick),
               netname='VSS', gridname=rg_m3m4_basic_thick)
    laygen.pin(name='VDD1', layer=laygen.layers['pin'][4], xy=laygen.get_xy(rvdd1, rg_m3m4_basic_thick),
               netname='VDD', gridname=rg_m3m4_basic_thick)
    for pn, p in sf_pins.items():
        if pn.startswith('VSS'):
            pxyl=pdict_m3m4_bt[isfl.name][pn]
            pxyr=pdict_m3m4_bt[isfr.name][pn]
            laygen.via(None, np.array([pxyl[0][0], ref_y-1]), gridname=rg_m3m4_basic_thick)
            laygen.via(None, np.array([pxyr[0][0], ref_y-1]), gridname=rg_m3m4_basic_thick)
        if pn.startswith('VDD'):
            pxyl=pdict_m3m4_bt[isfl.name][pn]
            pxyr=pdict_m3m4_bt[isfr.name][pn]
            laygen.via(None, np.array([pxyl[0][0], ref_y]), gridname=rg_m3m4_basic_thick)
            laygen.via(None, np.array([pxyr[0][0], ref_y]), gridname=rg_m3m4_basic_thick)

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
    rg_m1m2_thick = 'route_M1_M2_basic_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m2m3_thick = 'route_M2_M3_thick_basic'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m3m4_basic_thick = 'route_M3_M4_basic_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    #salatch generation (wboundary)
    cellname = 'sourceFollower_diff'
    print(cellname+" generating")
    mycell_list.append(cellname)
    m_sa=8
    m_rst_sa=8
    m_rgnn_sa=2
    m_buf_sa=8
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        m_mir=sizedict['sourceFollower']['m_mirror']
        m_bias=sizedict['sourceFollower']['m_bias']
        m_in=sizedict['sourceFollower']['m_in']
        m_ofst=sizedict['sourceFollower']['m_off']
        m_in_dum=sizedict['sourceFollower']['m_in_dum']
        m_bias_dum=sizedict['sourceFollower']['m_bias_dum']
        m_byp=sizedict['sourceFollower']['m_byp']
        m_byp_bias=sizedict['sourceFollower']['m_byp_bias']

    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)

    sf_origin=np.array([0, 0])

    #source follwer generation
    generate_source_follower_diff(laygen, objectname_pfix='SF0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                             devname_mos_boundary='nmos4_fast_boundary', devname_mos_body='nmos4_fast_center_nf2',
                             devname_mos_dmy='nmos4_fast_dmy_nf2', devname_tap_boundary='ptap_fast_boundary', devname_tap_body='ptap_fast_center_nf2',
                             devname_mos_space_4x='nmos4_fast_space_nf4', devname_mos_space_2x='nmos4_fast_space_nf2', devname_mos_space_1x='nmos4_fast_space',
                             devname_tap_space_4x='ptap_fast_space_nf4', devname_tap_space_2x='ptap_fast_space_nf2', devname_tap_space_1x='ptap_fast_space',
                             m_mir=m_mir, m_bias=m_bias, m_in=m_in,
                             m_ofst=m_ofst, m_bias_dum=m_bias_dum, m_in_dum=m_in_dum, m_byp=m_byp, m_byp_bias=m_byp_bias,
                             origin=sf_origin)
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
