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

def generate_tisaradc_body_core(laygen, objectname_pfix, ret_libname, sar_libname, clkdist_libname, space_1x_libname, ret_name, sar_name, clkdist_name, space_1x_name,
                                placement_grid,
                                routing_grid_m3m4, routing_grid_m4m5, routing_grid_m4m5_basic_thick, routing_grid_m5m6, routing_grid_m5m6_thick, 
                                routing_grid_m5m6_thick_basic, routing_grid_m6m7_thick,
                                num_bits=9, num_slices=8, use_offset=True, clkin_trackm=12, clk_cdac_bits=5, clk_pulse=False,
                                clkdist_offset=2, ret_use_laygo=True, use_sf=False, vref_sf=False, origin=np.array([0, 0])):
    """generate sar array """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    rg_m6m7_thick = routing_grid_m6m7_thick

    # placement
    space_size = laygen.templates.get_template(space_1x_name, libname=space_1x_libname).size
    # ret/sar/clk
    iret = laygen.place(name="I" + objectname_pfix + 'RET0', templatename=ret_name,
                      gridname=pg, xy=origin, template_libname=ret_libname)
    sar_xy = origin + (laygen.get_xy(obj=laygen.get_template(name = ret_name, libname=ret_libname), gridname=pg) * np.array([0, 1]))
    isar = laygen.relplace(name="I" + objectname_pfix + 'SAR0', templatename=sar_name,
                      gridname=pg, refinstname=iret.name, direction='top', template_libname=sar_libname)
    # clkdist_offset_pg=int(clkdist_offset*space_size[1]/laygen.get_grid(pg).height)
    # clkdist_xy = laygen.get_xy(obj =isar, gridname=pg) \
    #              + (laygen.get_xy(obj=laygen.get_template(name = sar_name, libname=sar_libname), gridname=pg) * np.array([0, 1])) \
    #              + np.array([0, clkdist_offset_pg])
    clkdist_xy = laygen.templates.get_template(clkdist_name, libname=clkdist_libname).xy
    clkdist_off_y = laygen.grids.get_absgrid_y(pg, clkdist_xy[0][1])
    clkdist_off_y_voff_route_phy = int(laygen.grids.get_phygrid_y(rg_m5m6, num_hori * num_vert+4) / \
                                       laygen.get_template_size('space_1x', gridname=None, libname=logictemplib)[1]+1) * \
                                   laygen.get_template_size('space_1x', gridname=None, libname=logictemplib)[1]
    clkdist_off_y_voff_route = laygen.grids.get_absgrid_y(pg, clkdist_off_y_voff_route_phy)

    iclkdist = laygen.relplace(name="I" + objectname_pfix + 'CLKDIST0', templatename=clkdist_name,
                        gridname=pg, refinstname=isar.name, direction='top',
                        xy=[0, -clkdist_off_y+clkdist_off_y_voff_route], template_libname=clkdist_libname)


    sar_template = laygen.templates.get_template(sar_name, sar_libname)
    sar_pins=sar_template.pins
    sar_xy=isar.xy
    ret_template = laygen.templates.get_template(ret_name, ret_libname)
    ret_pins=ret_template.pins
    ret_xy=iret.xy
    clkdist_template = laygen.templates.get_template(clkdist_name, clkdist_libname)
    clkdist_pins=clkdist_template.pins
    clkdist_xy=iclkdist.xy

    #prboundary
    sar_size = laygen.templates.get_template(sar_name, libname=sar_libname).size
    ret_size = laygen.templates.get_template(ret_name, libname=ret_libname).size
    clkdist_size = laygen.templates.get_template(clkdist_name, libname=clkdist_libname).size
    size_x=max((sar_size[0], ret_size[0]))
    print(sar_size[1]+ret_size[1]+clkdist_size[1], sar_size[1],ret_size[1],clkdist_size[1],space_size[1])
    size_y=int((sar_size[1]+ret_size[1]+clkdist_size[1])/space_size[1]+1+clkdist_offset)*space_size[1]
    laygen.add_rect(None, np.array([origin, origin+np.array([size_x, size_y])]), laygen.layers['prbnd'])

    pdict_m2m3=laygen.get_inst_pin_xy(None, None, rg_m2m3)
    pdict_m3m4=laygen.get_inst_pin_xy(None, None, rg_m3m4)
    pdict_m4m5=laygen.get_inst_pin_xy(None, None, rg_m4m5)
    pdict_m4m5_basic_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_basic_thick)
    pdict_m4m5_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_thick)
    pdict_m5m6=laygen.get_inst_pin_xy(None, None, rg_m5m6)
    pdict_m5m6_thick=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    pdict_m5m6_thick_basic=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick_basic)

    #VDD/VSS pins for sar and ret (just duplicate from lower hierarchy cells)
    vddsampcnt=0
    vddsarcnt=0
    vsscnt=0
    for pn, p in sar_pins.items():
        if pn.startswith('VDDSAMP'):
            pxy=sar_xy+sar_pins[pn]['xy']
            laygen.add_pin('VDDSAMP' + str(vddsampcnt), 'VDDSAMP:', pxy, sar_pins[pn]['layer'])
            vddsampcnt+=1
        if pn.startswith('VDDSAR'):
            pxy=sar_xy+sar_pins[pn]['xy']
            laygen.add_pin('VDDSAR' + str(vddsarcnt), 'VDDSAR:', pxy, sar_pins[pn]['layer'])
            vddsarcnt+=1
        if pn.startswith('VSS'):
            pxy=sar_xy+sar_pins[pn]['xy']
            laygen.add_pin('VSS' + str(vsscnt), 'VSS:', pxy, sar_pins[pn]['layer'])
            if pn=='VSS4':
                print(pn, vsscnt, p)
            vsscnt+=1
    for pn, p in ret_pins.items():
        if pn.startswith('VDD'):
            pxy=ret_xy+ret_pins[pn]['xy']
            laygen.add_pin('VDDSAR' + str(vddsarcnt), 'VDDSAR:', pxy, ret_pins[pn]['layer'])
            vddsarcnt+=1
        if pn.startswith('VSS'):
            pxy=ret_xy+ret_pins[pn]['xy']
            laygen.add_pin('VSS' + str(vsscnt), 'VSS:', pxy, ret_pins[pn]['layer'])
            vsscnt+=1
    for pn, p in clkdist_pins.items():
        if pn.startswith('VDD'):
            pxy = clkdist_xy + clkdist_pins[pn]['xy']
            laygen.add_pin('VDDSAMP' + str(vddsampcnt), 'VDDSAMP:', pxy, clkdist_pins[pn]['layer'])
            vddsampcnt += 1
        if pn.startswith('VSS'):
            pxy = clkdist_xy + clkdist_pins[pn]['xy']
            laygen.add_pin('VSS' + str(vsscnt), 'VSS:', pxy, clkdist_pins[pn]['layer'])
            vsscnt += 1
    # #VDD/VSS pins for clkdist
    # rvdd_ckd_m5=[]
    # rvss_ckd_m5=[]
    # for i in range(num_slices):
    #     rvdd, rvss = laygenhelper.generate_power_rails_from_rails_inst(laygen, routename_tag='', layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'],
    #         direction='y', input_rails_instname=iclkdist.name, input_rails_pin_prefix=['VDD0_'+str(i), 'VSS0_'+str(i)], generate_pin=False,
    #         overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None, offset_start_index=1, offset_end_index=-1)
    #     rvdd_ckd_m5+=rvdd
    #     rvss_ckd_m5+=rvss
    #     rvdd, rvss = laygenhelper.generate_power_rails_from_rails_inst(laygen, routename_tag='', layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'],
    #         direction='y', input_rails_instname=iclkdist.name, input_rails_pin_prefix=['VDD1_'+str(i), 'VSS1_'+str(i)], generate_pin=False,
    #         overwrite_start_coord=None, overwrite_end_coord=None, overwrite_num_routes=None, offset_start_index=1, offset_end_index=-1)
    #     rvdd_ckd_m5+=rvdd
    #     rvss_ckd_m5+=rvss
    # laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_CLKD_', layer=laygen.layers['pin'][6], gridname=rg_m5m6_thick, netnames=['VDDSAMP:', 'VSS:'], direction='x',
    #                                      input_rails_rect=[rvdd_ckd_m5, rvss_ckd_m5], generate_pin=True,
    #                                      overwrite_start_coord=0, overwrite_end_coord=None, overwrite_num_routes=None,
    #                                      offset_start_index=0, offset_end_index=0)

    #input pins
    if input_htree == False:
        #make virtual grids and route on the grids (assuming drc clearance of each block)
        rg_m5m6_thick_temp_sig='route_M5_M6_thick_temp_sig'
        laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_sig,
                                              instname=isar.name,
                                              inst_pin_prefix=['INP', 'INM'], xy_grid_type='xgrid')
        pdict_m5m6_thick_temp_sig = laygen.get_inst_pin_xy(None, None, rg_m5m6_thick_temp_sig)
        inp_x_list=[]
        inm_x_list=[]
        num_input_track=4
        in_x0 = pdict_m5m6_thick_temp_sig[isar.name]['INP0'][0][0]
        in_x1 = pdict_m5m6_thick_temp_sig[isar.name]['INM0'][0][0]
        in_y0 = pdict_m5m6_thick_temp_sig[isar.name]['INP0'][0][1]
        in_y1 = in_y0+2
        in_y2 = in_y1+2*num_input_track
        for i in range(num_slices):
            in_x0 = min(in_x0, pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0])
            in_x1 = max(in_x1, pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0])
            laygen.route(None, laygen.layers['metal'][5],
                         xy0=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0], in_y0]),
                         xy1=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0], in_y2]),
                         gridname0=rg_m5m6_thick_temp_sig)
            laygen.route(None, laygen.layers['metal'][5],
                         xy0=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0], in_y0]),
                         xy1=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0], in_y2]),
                         gridname0=rg_m5m6_thick_temp_sig)
            for j in range(num_input_track):
                laygen.via(None,np.array([pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0], in_y1+2*j]), rg_m5m6_thick_temp_sig)
                laygen.via(None,np.array([pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0], in_y1+2*j+1]), rg_m5m6_thick_temp_sig)
        #in_x0 -= 2
        #in_x1 += 2
        rinp=[]
        rinm=[]
        for i in range(num_input_track):
            rinp.append(laygen.route(None, laygen.layers['metal'][6], xy0=np.array([in_x0, in_y1+2*i]), xy1=np.array([in_x1, in_y1+2*i]), gridname0=rg_m5m6_thick_temp_sig))
            rinm.append(laygen.route(None, laygen.layers['metal'][6], xy0=np.array([in_x0, in_y1+2*i+1]), xy1=np.array([in_x1, in_y1+2*i+1]), gridname0=rg_m5m6_thick_temp_sig))
            laygen.add_pin('INP' + str(i), 'INP', rinp[-1].xy, laygen.layers['pin'][6])
            laygen.add_pin('INM' + str(i), 'INM', rinm[-1].xy, laygen.layers['pin'][6])
    else:
        for i in range(num_slices):
            pn = 'INP' + str(i)
            laygen.pin(name=pn, layer=laygen.layers['pin'][5], xy=pdict_m4m5_thick[isar.name][pn], gridname=rg_m4m5_thick)
            pn = 'INM' + str(i)
            laygen.pin(name=pn, layer=laygen.layers['pin'][5], xy=pdict_m4m5_thick[isar.name][pn], gridname=rg_m4m5_thick)

    #clk output pins
    #laygen.add_pin('CLKBOUT_NC', 'CLKBOUT_NC', np.array([sar_xy, sar_xy])+sar_pins['CLKO07']['xy'], sar_pins['CLKO07']['layer'])
    laygen.add_pin('CLKOUT_DES', 'CLKOUT_DES', ret_pins['ck_out']['xy'], ret_pins['ck_out']['layer'])
    
    #retimer output pins
    for i in range(num_slices):
        for j in range(num_bits):
            pn='out_'+str(i)+'<'+str(j)+'>'
            pn_out='ADCOUT'+str(i)+'<'+str(j)+'>'
            xy=pdict_m3m4[iret.name][pn]
            xy[0][1]=0
            r=laygen.route(None, layer=laygen.layers['metal'][3], xy0=xy[0], xy1=xy[1], gridname0=rg_m3m4)
            laygen.boundary_pin_from_rect(r, rg_m3m4, pn_out, laygen.layers['pin'][3], size=4,
                                          direction='bottom')
    #extclk_sel pins
    for i in range(num_slices):
            pn='EXTSEL_CLK'+str(i)
            pn_out='EXTSEL_CLK'+str(i)
            xy=pdict_m5m6[isar.name][pn]
            xy[0][1]=0
            r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=xy[0], xy1=xy[1], gridname0=rg_m5m6)
            laygen.boundary_pin_from_rect(r, rg_m5m6, pn_out, laygen.layers['pin'][5], size=4,
                                          direction='bottom')
    #asclkd pins
    for i in range(num_slices):
        for j in range(4):
            pn='ASCLKD'+str(i)+'<'+str(j)+'>'
            pn_out='ASCLKD'+str(i)+'<'+str(j)+'>'
            xy=pdict_m5m6[isar.name][pn]
            xy[0][1]=0 
            r=laygen.route(None, layer=laygen.layers['metal'][5], xy0=xy[0], xy1=xy[1], gridname0=rg_m5m6)
            laygen.boundary_pin_from_rect(r, rg_m5m6, pn_out, laygen.layers['pin'][5], size=4,
                                          direction='bottom')

    # MODESEL pins
    if clkgen_mode == True:
        for i in range(num_slices):
            pn = 'MODESEL' + str(i)
            pn_out = 'MODESEL' + str(i)
            xy = pdict_m5m6[isar.name][pn]
            xy[0][1] = 0
            r = laygen.route(None, layer=laygen.layers['metal'][5], xy0=xy[0], xy1=xy[1], gridname0=rg_m5m6)
            laygen.boundary_pin_from_rect(r, rg_m5m6, pn_out, laygen.layers['pin'][5], size=4,
                                          direction='bottom')
    #osp/osm pins
    if use_offset == True:
        for i in range(num_slices):
            laygen.pin(name='OSP' + str(i), layer=laygen.layers['pin'][4], xy=pdict_m4m5[isar.name]['OSP' + str(i)], gridname=rg_m4m5)
            laygen.pin(name='OSM' + str(i), layer=laygen.layers['pin'][4], xy=pdict_m4m5[isar.name]['OSM' + str(i)], gridname=rg_m4m5)
    #vref pins
    num_vref_routes=4
    for i in range(num_vref_routes):
        laygen.pin(name='VREF' + str(i) + '<0>', layer=laygen.layers['pin'][6], xy=pdict_m5m6_thick[isar.name]['VREF<0>_M6_' + str(i)], gridname=rg_m5m6_thick, netname='VREF<0>')
        laygen.pin(name='VREF' + str(i) + '<1>', layer=laygen.layers['pin'][6], xy=pdict_m5m6_thick[isar.name]['VREF<1>_M6_' + str(i)], gridname=rg_m5m6_thick, netname='VREF<1>')
        laygen.pin(name='VREF' + str(i) + '<2>', layer=laygen.layers['pin'][6], xy=pdict_m5m6_thick[isar.name]['VREF<2>_M6_' + str(i)], gridname=rg_m5m6_thick, netname='VREF<2>')
    #clkcal pins
    for i in range(num_slices):
        for j in range(clk_cdac_bits):
            pn='CLKCAL'+str(i)+'<'+str(j)+'>'
            pxy=clkdist_xy+clkdist_pins[pn]['xy']
            laygen.add_pin(pn, pn, pxy, clkdist_pins[pn]['layer'])
    #clkin pins
    for i in range(clkin_trackm):
        pn='CLKIP'+'_'+str(i)
        nn='CLKIP'
        laygen.add_pin(pn, nn, clkdist_xy+clkdist_pins[pn]['xy'], clkdist_pins[pn]['layer'])
        pn='CLKIN'+'_'+str(i)
        nn='CLKIN'
        laygen.add_pin(pn, nn, clkdist_xy+clkdist_pins[pn]['xy'], clkdist_pins[pn]['layer'])
    laygen.add_pin('RSTP', 'RSTP', clkdist_xy+clkdist_pins['RSTP']['xy'], clkdist_pins['RSTP']['layer'])
    laygen.add_pin('RSTN', 'RSTN', clkdist_xy+clkdist_pins['RSTN']['xy'], clkdist_pins['RSTN']['layer'])

    # VREF SF pins
    if vref_sf == True:
        for pn, p in sar_pins.items():
            if pn.startswith('VREF_SF_'):
                for i in range(num_slices):
                    pxy = sar_xy + sar_pins[pn]['xy']
                    laygen.add_pin(pn, pn, pxy, sar_pins[pn]['layer'])
    # SF pins
    if use_sf == True:
        for pn, p in sar_pins.items():
            if pn.startswith('SF_'):
                for i in range(num_slices):
                    pxy = sar_xy + sar_pins[pn]['xy']
                    laygen.add_pin(pn, pn, pxy, sar_pins[pn]['layer'])

    #clkdist-sar routes (clock)
    #make virtual grids and route on the grids (assuming drc clearance of each block)
    # 1x pulsewidth
    rg_m4m5_temp='route_M4_M5_temp'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m4m5_basic_thick, gridname_output=rg_m4m5_temp,
                                          instname=isar.name,
                                          inst_pin_prefix=['CLK'], xy_grid_type='xgrid')
    pdict_m4m5_temp = laygen.get_inst_pin_xy(None, None, rg_m4m5_temp)
    # if clk_pulse == False:
    for i in range(num_slices):
        x0=pdict_m4m5[isar.name]['CLK'+str(i)][0][0]
        y1=pdict_m4m5[iclkdist.name]['CLKO'+str(i)+'<0>'][0][1]+4
        laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
                        xy0=pdict_m4m5[iclkdist.name]['CLKO'+str(i)+'<0>'][0],
                        xy1=np.array([x0, y1]), gridname0=rg_m4m5)
        # laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
        #                 xy0=pdict_m4m5[iclkdist.name]['CLKO'+str(i)+'<1>'][0],
        #                 xy1=np.array([x0, y1+2]), gridname=rg_m4m5)
        # laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
        #                 xy0=pdict_m4m5[iclkdist.name]['CLKO'+str(i)+'<0>'][0]+np.array([4,0]),
        #                 xy1=np.array([x0, y1+4]), gridname=rg_m4m5)
        # laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
        #                 xy0=pdict_m4m5[iclkdist.name]['CLKO'+str(i)+'<1>'][0]+np.array([4,0]),
        #                 xy1=np.array([x0, y1+6]), gridname=rg_m4m5)
        laygen.route(None, layer=laygen.layers['metal'][5],
                        xy0=pdict_m4m5_temp[isar.name]['CLK'+str(i)][0],
                        xy1=np.array([pdict_m4m5_temp[isar.name]['CLK'+str(i)][0][0], y1+0]),
                        gridname0=rg_m4m5_temp)
        laygen.via(None,np.array([pdict_m4m5_temp[isar.name]['CLK'+str(i)][0][0], y1]), rg_m4m5_temp)
        # laygen.via(None,np.array([pdict_m4m5_temp[isar.name]['CLK'+str(i)][0][0], y1+2]), rg_m4m5_temp)
        # laygen.via(None,np.array([pdict_m4m5_temp[isar.name]['CLK'+str(i)][0][0], y1+4]), rg_m4m5_temp)
        # laygen.via(None,np.array([pdict_m4m5_temp[isar.name]['CLK'+str(i)][0][0], y1+6]), rg_m4m5_temp)

    # # clock routing for TISAR: 2x pulsewidth
    # elif clk_pulse == True:
    #     for i in range(num_slices):
    #         laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
    #                         xy0=pdict_m4m5_basic_thick[isar.name]['CLK'+str(i)][0],
    #                         xy1=[pdict_m4m5[iclkdist.name]['CLKO%d<0>'%i][0][0]-3, pdict_m4m5[iclkdist.name]['DATAO<%d>'%i][0][1]-16],
    #                         track_y=pdict_m4m5[isar.name]['CLK'+str(i)][0][1]+3,
    #                         gridname0=rg_m4m5_basic_thick, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5, extendl=0, extendr=0)
    #         laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
    #                      xy0=[pdict_m4m5[iclkdist.name]['CLKO%d<0>'%i][0][0]-3, pdict_m4m5[iclkdist.name]['DATAO<%d>'%i][0][1]-16],
    #                      xy1=pdict_m3m4[iclkdist.name]['DATAO<%d>'%i][0],
    #                      track_y=pdict_m4m5[iclkdist.name]['DATAO<%d>'%i][0][1]-14,
    #                      gridname0=rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4, extendl=0, extendr=0)

    #sar-retimer routes (data)
    for i in range(num_slices):
        for j in range(num_bits):
            if ret_use_laygo == True:
                if j == num_bits-1:
                    laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
                                 xy0=pdict_m4m5[isar.name]['ADCOUT' + str(i) + '<' + str(j) + '>'][0],
                                 xy1=pdict_m4m5[iret.name]['in_' + str(i) + '<' + str(j) + '>'][0],
                                 track_y=pdict_m4m5[isar.name]['ADCOUT' + str(i) + '<' + str(j) + '>'][0][1] + j * 2 + 2,
                                 gridname0=rg_m4m5, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5, extendl=0, extendr=0)
                else:
                    laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
                                xy0=pdict_m4m5[isar.name]['ADCOUT'+str(i)+'<'+str(j)+'>'][0],
                                xy1=pdict_m3m4[iret.name]['in_'+str(i)+'<'+str(j)+'>'][0],
                                track_y=pdict_m4m5[isar.name]['ADCOUT'+str(i)+'<'+str(j)+'>'][0][1]+j*2+2,
                                gridname0=rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4, extendl=0, extendr=0)
            else:
                laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
                                 xy0=pdict_m4m5[isar.name]['ADCOUT' + str(i) + '<' + str(j) + '>'][0],
                                 xy1=pdict_m3m4[iret.name]['in_' + str(i) + '<' + str(j) + '>'][0],
                                 track_y=pdict_m4m5[isar.name]['ADCOUT' + str(i) + '<' + str(j) + '>'][0][
                                             1] + j * 2 + 2,
                                 gridname0=rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4, extendl=0,
                                 extendr=0)

    #sar-retimer routes (clock)
    #finding clock_bar phases <- added by Jaeduk
    #rules:
    # 1) last stage latches: num_slices-1
    # 2) second last stage latches: int(num_slices/2)-1
    # 3) the first half of first stage latches: int((int(num_slices/2)+1)%num_slices)
    # 4) the second half of first stage latches: 1
    # 5) the output phase = the second last latch phase
    if num_slices > 4:
        ck_phase_2 = num_slices - 1
        ck_phase_1 = int(num_slices / 2) - 1
        ck_phase_0_0 = int((int(num_slices / 2) + 1) % num_slices)
        ck_phase_0_1 = 1
    elif num_slices == 4:
        ck_phase_2 = 2
        ck_phase_1 = 0
        ck_phase_0_0 = 3
        ck_phase_0_1 = 1
    ck_phase_out=ck_phase_1
    ck_phase_buf=sorted(set([ck_phase_2, ck_phase_1, ck_phase_0_0, ck_phase_0_1]))
    rg_m3m4_temp_clk='route_M3_M4_basic_temp_clk'
    laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m3m4, gridname_output=rg_m3m4_temp_clk,
                                          instname=iret.name, 
                                          inst_pin_prefix=['clk'+str(i) for i in ck_phase_buf], xy_grid_type='xgrid')
    pdict_m3m4_temp_clk = laygen.get_inst_pin_xy(None, None, rg_m3m4_temp_clk)
    for i in ck_phase_buf:
        for j in range(1):
            laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
                            xy0=pdict_m4m5[isar.name]['CLKO0'+str(i)][0], 
                            xy1=pdict_m3m4_temp_clk[iret.name]['clk'+str(i)][0], 
                            track_y=pdict_m4m5[isar.name]['CLKO00'][0][1]+num_bits*2+2+2*j+2*(ck_phase_buf.index(i)),
                            gridname0=rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4_temp_clk, extendl=0, extendr=0)
            laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4], 
                            xy0=pdict_m4m5[isar.name]['CLKO1'+str(i)][0], 
                            xy1=pdict_m3m4_temp_clk[iret.name]['clk'+str(i)][0], 
                            track_y=pdict_m4m5[isar.name]['CLKO00'][0][1]+num_bits*2+2+2*j+2*(ck_phase_buf.index(i)),
                            gridname0=rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4_temp_clk, extendl=0, extendr=0)
        r=laygen.route(None, layer=laygen.layers['metal'][3], xy0=pdict_m3m4_temp_clk[iret.name]['clk'+str(i)][0], 
                        xy1=np.array([pdict_m3m4_temp_clk[iret.name]['clk'+str(i)][0][0], 
                                      pdict_m4m5[isar.name]['CLKO00'][0][1]+num_bits*2+2+2*4+1]), gridname0=rg_m3m4_temp_clk)

if __name__ == '__main__':
    laygen = laygo.GridLayoutGenerator(config_file="laygo_config.yaml")

    import imp
    try:
        imp.find_module('bag')
        laygen.use_phantom = False
    except ImportError:
        laygen.use_phantom = True

    mycell_list = []
    num_bits = 9
    num_slices = 9
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
        num_slices=specdict['n_interleave']
        use_offset=specdict['use_offset']
        ret_use_laygo=specdict['ret_use_laygo']
        clkin_trackm=sizedict['clk_dis_htree']['m_track']
        clk_cdac_bits = sizedict['clk_dis_cdac']['num_bits']
        clk_pulse=specdict['clk_pulse_overlap']
        use_sf = specdict['use_sf']
        vref_sf = specdict['use_vref_sf']
        input_htree = specdict['input_htree']
        num_hori=sizedict['r2rdac_array']['num_hori']
        num_vert=sizedict['r2rdac_array']['num_vert']
        clkgen_mode = sizedict['sarclkgen']['mux_fast']

    tech=laygen.tech
    utemplib = tech+'_microtemplates_dense'
    logictemplib = tech+'_logic_templates'
    if ret_use_laygo == False:
        ret_libname = 'adc_retimer_ec'
        laygen.load_template(filename='adc_retimer.yaml', libname=ret_libname)
    elif ret_use_laygo == True:
        ret_libname = 'adc_sar_generated'
        laygen.load_template(filename=ret_libname + '.yaml', libname=ret_libname)
    clkdist_libname = 'clk_dis_generated'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    laygen.load_template(filename=clkdist_libname+'.yaml', libname=clkdist_libname)
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
    rg_m5m6_thick_basic = 'route_M5_M6_thick_basic'
    rg_m5m6_thick2_thick = 'route_M5_M6_thick2_thick'
    rg_m6m7_thick = 'route_M6_M7_thick'
    rg_m6m7_thick2_thick = 'route_M6_M7_thick2_thick'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'


    cellname = 'tisaradc_body_core'
    sar_name = 'sar_wsamp_array'
    #sar_name = 'sar_wsamp_'+str(num_bits)+'b_array_'+str(num_slices)+'slice'
    ret_name = 'adc_retimer'
    clkdist_name = 'clk_dis_viadel_htree'
    #tisar_space_name = 'tisaradc_body_space'
    space_1x_name = 'space_1x'

    #sar generation
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_tisaradc_body_core(laygen, objectname_pfix='TISA0', 
                 ret_libname=ret_libname, sar_libname=workinglib, clkdist_libname=clkdist_libname, space_1x_libname=logictemplib,
                 ret_name=ret_name, sar_name=sar_name, clkdist_name=clkdist_name, space_1x_name=space_1x_name,
                 placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick,
                 routing_grid_m5m6=rg_m5m6,
                 routing_grid_m5m6_thick=rg_m5m6_thick, 
                 routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic, 
                 routing_grid_m6m7_thick=rg_m6m7_thick,
                 num_bits=num_bits, num_slices=num_slices, use_offset=use_offset, clkin_trackm=clkin_trackm, clk_cdac_bits=clk_cdac_bits,
                 clk_pulse=clk_pulse, clkdist_offset=2, ret_use_laygo=ret_use_laygo, vref_sf=vref_sf, use_sf=use_sf, origin=np.array([0, 0]))
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
