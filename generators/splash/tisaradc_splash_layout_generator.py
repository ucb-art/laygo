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

def generate_tisaradc_splash(laygen, objectname_pfix, ret_libname, sar_libname, clkdist_libname, rdac_libname, space_1x_libname, ret_name,
                             sar_name, clkdist_name, rdac_name, space_1x_name, placement_grid,
                                routing_grid_m3m4, routing_grid_m4m5, routing_grid_m4m5_basic_thick, routing_grid_m5m6, routing_grid_m5m6_thick,
                                routing_grid_m5m6_basic_thick, routing_grid_m5m6_thick_basic,
                                routing_grid_m6m7_thick, routing_grid_m7m8_thick,
                                num_inv_bb, num_bits=9, num_slices=8, clk_pulse=True, slice_order=[0, 1], trackm=4, origin=np.array([0, 0])):
    """generate sar array """
    pg = placement_grid

    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5
    rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    rg_m5m6 = routing_grid_m5m6
    rg_m5m6_thick = routing_grid_m5m6_thick
    rg_m5m6_basic_thick = routing_grid_m5m6_basic_thick
    rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    rg_m6m7_thick = routing_grid_m6m7_thick
    rg_m7m8_thick = routing_grid_m7m8_thick

    # placement
    # ret/sar/clk
    # sar_slice_size = laygen.templates.get_template(sar_slice_name, libname=sar_libname).size
    bnd_size = laygen.get_template('boundary_bottom', libname=utemplib).size
    sar_slice_size = laygen.get_template_size(sar_slice_name, pg, libname=sar_libname)
    clkcal_size = laygen.templates.get_template(clkcal_name, libname=clkdist_libname).size
    # ret_offset = laygen.get_template_size('boundary_bottomleft', pg, libname=utemplib)[0]
    ret_offset = 0
    clkdist_xy = laygen.templates.get_template(clkdist_name, libname=clkdist_libname).xy
    clkdist_off_y = laygen.grids.get_absgrid_y(pg, clkdist_xy[0][1])
    clkdist_off_y_voff_route_phy = int(laygen.grids.get_phygrid_y(rg_m5m6, num_hori * num_vert+4) / \
                                       laygen.get_template_size('space_1x', gridname=None, libname=logictemplib)[1]+1) * \
                                   laygen.get_template_size('space_1x', gridname=None, libname=logictemplib)[1]
    clkdist_off_y_voff_route = laygen.grids.get_absgrid_y(pg, clkdist_off_y_voff_route_phy)
    # clkdist_xy =laygen.get_template_xy(clkdist_name, pg, libname=clkdist_libname)
    clkcal_xy = laygen.templates.get_template(clkcal_name, libname=clkdist_libname).xy
    clkcal_y = laygen.get_template_size(ret_name, pg, libname=ret_libname)[1] + \
               laygen.get_template_size(sar_name, pg, libname=sar_libname)[1] + \
               laygen.get_template_size(clkdist_name, pg, libname=clkdist_libname)[1] + \
               laygen.grids.get_absgrid_y(pg, clkcal_xy[1][1]) + \
               clkdist_off_y_voff_route
    rdac_xy = laygen.templates.get_template(rdac_name, libname=rdac_libname).xy
    rdac_off_x = laygen.grids.get_absgrid_x(pg, rdac_xy[1][0])
    htree_off_y = laygen.get_template_pin_xy(htree_name, 'VSS_0_0', rg_m7m8_thick, libname=workinglib)[0][1]-2
    num_input_shield_track = 1 # defined in tisar_htree_diff_m7m8, to be parameterized
    dcap_off_y = max(laygen.get_template_size(rdac_name, pg, libname=rdac_libname)[1], clkcal_y+laygen.grids.get_absgrid_y(pg, clkcal_xy[1][1]))
    dcap_xy = np.array([-rdac_off_x, dcap_off_y])
    if num_input_shield_track == 2:
        htree_off_x = laygen.get_template_pin_xy(htree_name, 'VSS_0_0', rg_m7m8_thick, libname=workinglib)[0][0]/2 + \
                      laygen.get_template_pin_xy(htree_name, 'VSS_0_1', rg_m7m8_thick, libname=workinglib)[0][0]/2 - \
                      int(laygen.get_template_size(sar_slice_name, rg_m7m8_thick, libname=workinglib)[0]/2)
    elif num_input_shield_track == 1:
        htree_off_x = laygen.get_template_pin_xy(htree_name, 'VSS_0_0', rg_m7m8_thick, libname=workinglib)[0][0] - \
                      int(laygen.get_template_size(sar_slice_name, rg_m7m8_thick, libname=workinglib)[0]/2+0.5)

    iret = laygen.place(name="I" + objectname_pfix + 'RET0', templatename=ret_name,
                      gridname=pg, xy=origin-[ret_offset,0], template_libname=ret_libname)
    sar_xy = origin + (laygen.get_template_size(ret_name, gridname=pg, libname=ret_libname)*np.array([0,1]) )
    isar = laygen.relplace(name="I" + objectname_pfix + 'SAR0', templatename=sar_name,
                      gridname=pg, xy=sar_xy, template_libname=sar_libname)
    isarcal1 = laygen.relplace(name="I" + objectname_pfix + 'SARCAL1', templatename=sar_slice_name,
                           gridname=pg, refinstname=isar.name, direction='right', template_libname=sar_libname)
    isarcal0 = laygen.relplace(name="I" + objectname_pfix + 'SARCAL0', templatename=sar_slice_name,
                               gridname=pg, refinstname=isarcal1.name, direction='right', template_libname=sar_libname)
    iclkdist = laygen.relplace(name="I" + objectname_pfix + 'CLKDIST0', templatename=clkdist_name,
                        gridname=pg, refinstname=isar.name, direction='top',
                        xy=[0, -clkdist_off_y+clkdist_off_y_voff_route], template_libname=clkdist_libname)
    iclkcal = laygen.relplace(name="I" + objectname_pfix + 'CLKCAL0', templatename=clkcal_name,
                      gridname=pg, transform='MX',
                      xy=[sar_slice_size[0]*2/2, clkcal_y],
                      template_libname=clkdist_libname)
    irdac = laygen.relplace(name="I" + objectname_pfix + 'RDAC0', templatename=rdac_name,
                      gridname=pg, transform='R0', xy=[-rdac_off_x, 0],
                      template_libname=rdac_libname)
    ihtree_in = laygen.relplace(name="I" + objectname_pfix + 'HTREE0', templatename=htree_name,
                      gridname=rg_m7m8_thick, transform='MX', xy=[-htree_off_x, htree_off_y],
                      template_libname=workinglib)
    idcap = laygen.relplace(name="I" + objectname_pfix + 'DCAP0', templatename='tisaradc_dcap_array',
                      gridname=pg, transform='R0', xy=dcap_xy,
                      template_libname=sar_libname)

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
    # sar_size = laygen.templates.get_template(sar_name, libname=sar_libname).size
    # ret_size = laygen.templates.get_template(ret_name, libname=ret_libname).size
    space_size = laygen.templates.get_template('boundary_bottom', libname=utemplib).size
    # clkdist_size = laygen.templates.get_template(clkdist_name, libname=clkdist_libname).size+clkdist_offset
    # clkcal_size = laygen.templates.get_template(clkcal_name, libname=clkdist_libname).size
    size_x=iclkcal.xy[0]+iclkcal.size[0]
    size_y=int((iclkcal.xy[1]-laygen.templates.get_template(clkcal_name, libname=clkdist_libname).xy[0][1])/space_size[1]+1)*space_size[1]
    laygen.add_rect(None, np.array([origin, origin+np.array([size_x, size_y])]), laygen.layers['prbnd'])

    # Routing

    pdict_m2m3=laygen.get_inst_pin_xy(None, None, rg_m2m3)
    pdict_m3m4=laygen.get_inst_pin_xy(None, None, rg_m3m4)
    pdict_m4m5=laygen.get_inst_pin_xy(None, None, rg_m4m5)
    pdict_m4m5_basic_thick=laygen.get_inst_pin_xy(None, None, rg_m4m5_basic_thick)
    pdict_m5m6=laygen.get_inst_pin_xy(None, None, rg_m5m6)
    pdict_m5m6_thick=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    pdict_m5m6_thick_basic=laygen.get_inst_pin_xy(None, None, rg_m5m6_thick_basic)

    # Input clock routing
    # CLKCAL clk route
    ref_y = laygen.grids.get_absgrid_y(rg_m4m5, iclkcal.xy[1] -
                                       laygen.templates.get_template(clkcal_name, libname=clkdist_libname).xy[1][1])
    ref_x0 = pdict_m4m5[iclkcal.name]['CLKI0_%d'%(trackm-1)][0][0]
    ref_x1 = ref_x0 + laygen.get_template_size('clk_dis_viadel_cell', rg_m4m5,'clk_dis_generated')[0]*num_slices
    for i in range(trackm):
        rclkcal = laygen.route(None, laygen.layers['metal'][4],
                        xy0=[ref_x0, ref_y+2*i+1], xy1=[ref_x1, ref_y+2*i+1], gridname0=rg_m4m5)
        # laygen.pin_from_rect('CLKIP_M4' + str(i), laygen.layers['pin'][4], rclkcal, rg_m4m5, netname='CLKIP')
    # ADD CLKB horizontal wires
    ref_xy_m4m5 = pdict_m4m5[iclkcal.name]['CLKI0_%d'%(trackm-1)][0]
    # ref_x1_m4m5 = laygen.grids.get_absgrid_x(rg_m4m5, size_x)
    for i in range(trackm): #M4
        rh = laygen.route(None, laygen.layers['metal'][4], xy0=ref_xy_m4m5 - [0, i*2 + 2*trackm + 8],
                     xy1=[ref_x1, ref_xy_m4m5[1]-i*2-2*trackm-8], gridname0=rg_m4m5)
        # laygen.pin_from_rect('CLKIN_M4'+str(i), laygen.layers['pin'][4], rh, rg_m4m5, netname='CLKIN')
    # Extend M5 from clkdist
    clkdist_template = laygen.templates.get_template(clkdist_name, clkdist_libname)
    clkdist_pins = clkdist_template.pins
    ref_xy_m5m6 = laygen.get_inst_pin_xy(iclkcal.name, 'CLKI0_%d' % (trackm - 1), rg_m5m6_basic_thick)[0]
    ref_x1_m5m6 = laygen.grids.get_absgrid_x(rg_m5m6_basic_thick, size_x)
    track_m_m6 = 10
    for pn, p in clkdist_pins.items():
        if pn.startswith('CLKIP'):
            pxy=laygen.get_inst_pin_xy(iclkdist.name, pn, rg_m4m5)
            laygen.route(None, laygen.layers['metal'][5], xy0=pxy[0],
                         xy1=[pxy[0][0], ref_xy_m4m5[1]-4], gridname0=rg_m4m5)
            # ADD m4m5 vias
            for i in range(trackm):
                laygen.via(None, xy=[pxy[0][0], ref_xy_m4m5[1]-2*i-4], gridname=rg_m4m5)
            # ADD m5m6 vias
            for i in range(track_m_m6):
                laygen.via(None, xy=[pxy[0][0], ref_xy_m5m6[1] - (i + 2)],
                           gridname=rg_m5m6_basic_thick)
        if pn.startswith('CLKIN'):
            pxy = laygen.get_inst_pin_xy(iclkdist.name, pn, rg_m4m5)
            laygen.route(None, laygen.layers['metal'][5], xy0=pxy[0],
                         xy1=[pxy[0][0], ref_xy_m4m5[1]-4], gridname0=rg_m4m5)
            # ADD m4m5 vias
            for i in range(trackm):
                laygen.via(None, xy=[pxy[0][0], ref_xy_m4m5[1] - 2 * i - 0 - (2*trackm + 8)], gridname=rg_m4m5)
            # ADD m5m6 vias
            for i in range(track_m_m6):
                laygen.via(None, xy=[pxy[0][0], ref_xy_m5m6[1] - (i + track_m_m6 + 2 + 3)], gridname=rg_m5m6_basic_thick)
    # M6 tracks
    for i in range(track_m_m6):
        rckp = laygen.route(None, laygen.layers['metal'][6], xy0=ref_xy_m5m6 - [0, i+2],
        # rckp = laygen.route(None, laygen.layers['metal'][6], xy0= [0, ref_xy_m5m6[1] - (i+2)],
                     xy1=[ref_x1_m5m6, ref_xy_m5m6[1]-i-2], gridname0=rg_m5m6_basic_thick)
        rckn = laygen.route(None, laygen.layers['metal'][6], xy0=ref_xy_m5m6 - [0, i + track_m_m6 + 2 + 3],
        # rckn = laygen.route(None, laygen.layers['metal'][6], xy0=[0, ref_xy_m5m6[1] - i - track_m_m6 - 2 - 3],
                        xy1=[ref_x1_m5m6, ref_xy_m5m6[1] - i - track_m_m6 - 2 - 3], gridname0=rg_m5m6_basic_thick)
        laygen.pin_from_rect('CLKIP_M6' + str(i), laygen.layers['pin'][6], rckp, rg_m5m6_basic_thick, netname='CLKIP')
        laygen.pin_from_rect('CLKIN_M6' + str(i), laygen.layers['pin'][6], rckn, rg_m5m6_basic_thick, netname='CLKIN')

    # clock routing for TISAR
    for i in range(num_slices):
        # laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
        #                 xy0=pdict_m4m5_basic_thick[isar.name]['CLK'+str(i)][0],
        #                 xy1=[pdict_m4m5[iclkdist.name]['CLKO%d<0>'%i][0][0]-3, pdict_m4m5[iclkdist.name]['DATAO<%d>'%i][0][1]-16],
        #                 track_y=pdict_m4m5[isar.name]['CLK'+str(i)][0][1]+3,
        #                 gridname=rg_m4m5_basic_thick, layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5, extendl=0, extendr=0)
        # laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
        #              xy0=[pdict_m4m5[iclkdist.name]['CLKO%d<0>'%i][0][0]-3, pdict_m4m5[iclkdist.name]['DATAO<%d>'%i][0][1]-16],
        #              xy1=pdict_m4m5[iclkdist.name]['DATAO<%d>'%i][0],
        #              track_y=pdict_m4m5[iclkdist.name]['DATAO<%d>'%i][0][1]-14,
        #              gridname=rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4, extendl=0, extendr=0)
        x0 = pdict_m4m5[isar.name]['CLK' + str(i)][0][0]
        y1 = pdict_m4m5[iclkdist.name]['CLKO' + str(i) + '<0>'][0][1] + 4
        laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
                        xy0=pdict_m4m5[iclkdist.name]['CLKO' + str(i) + '<0>'][0],
                        xy1=np.array([x0, y1]), gridname0=rg_m4m5)
        laygen.route(None, layer=laygen.layers['metal'][5],
                     xy0=pdict_m4m5_basic_thick[isar.name]['CLK' + str(i)][0],
                     xy1=np.array([pdict_m4m5_basic_thick[isar.name]['CLK' + str(i)][0][0], y1 + 0]),
                     gridname0=rg_m4m5_basic_thick)
        laygen.via(None, np.array([pdict_m4m5_basic_thick[isar.name]['CLK' + str(i)][0][0], y1]), rg_m4m5_basic_thick)

    # ADC input route
    rinp_m7=[]
    rinm_m7=[]
    num_input_track = 2 # defined in tisar_htree_diff_m7m8, to be parameterized
    for i in range(num_slices):
        inp_xy_m5 = pdict_m5m6_thick[isar.name]['INP%d' % i][1]
        inm_xy_m5 = pdict_m5m6_thick[isar.name]['INM%d' % i][1]
        for j in range(num_input_track):
            inp_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WPO_' + str(slice_order.index(i)) + '_' + str(j), rg_m6m7_thick)[1]
            inm_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WNO_' + str(slice_order.index(i)) + '_' + str(j), rg_m6m7_thick)[1]
            laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                         xy0=inp_xy_m5, xy1=inp_xy_m7, track_y=inp_xy_m5[1]-3,
                         gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)
            laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                             xy0=inm_xy_m5, xy1=inm_xy_m7, track_y=inm_xy_m5[1]-2,
                             gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)
        for j in range(num_input_shield_track):
            for k in range(2):
                laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                             xy0=laygen.get_inst_pin_xy(iret.name, 'VSS' + str(2*i+k), rg_m5m6_thick)[1],
                             xy1=laygen.get_inst_pin_xy(ihtree_in.name, 'VSS_' + str(i) + '_' + str(j), rg_m6m7_thick)[1],
                             track_y=laygen.get_inst_pin_xy(ihtree_in.name, 'VSS_' + str(i) + '_' + str(j), rg_m6m7_thick)[0][1],
                             gridname0=rg_m5m6_thick, layerv1=laygen.layers['metal'][7], gridname1=rg_m6m7_thick)
    for j in range(num_input_track):
        inp_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WPI_' + str(j), rg_m6m7_thick)
        inm_xy_m7 = laygen.get_inst_pin_xy(ihtree_in.name, 'WNI_' + str(num_input_shield_track+num_input_track+j), rg_m6m7_thick)
        laygen.pin('INP_'+str(j), xy=inp_xy_m7, layer=laygen.layers['pin'][7], gridname=rg_m6m7_thick, netname='INP')
        laygen.pin('INM_' + str(j), xy=inm_xy_m7, layer=laygen.layers['pin'][7], gridname=rg_m6m7_thick, netname='INM')

    # for i in range(num_slices):
    #     inp_xy_m5 = pdict_m5m6_thick[isar.name]['INP%d' % i][1]
    #     inm_xy_m5 = pdict_m5m6_thick[isar.name]['INM%d' % i][1]
    #     rinp_m6 = laygen.route(None, laygen.layers['metal'][6],
    #                     xy0=inp_xy_m5+[-1,0], xy1=inm_xy_m5+[1,0], gridname0=rg_m5m6_thick, via0=[1,0])
    #     rinm_m6 = laygen.route(None, laygen.layers['metal'][6],
    #                        xy0=inp_xy_m5+[-1,1], xy1=inm_xy_m5+[1,1], gridname0=rg_m5m6_thick, via1=[-1, 0])
    #     inp_xy_m6 = laygen.get_rect_xy(rinp_m6.name, rg_m6m7_thick)
    #     inm_xy_m6 = laygen.get_rect_xy(rinm_m6.name, rg_m6m7_thick)
    #     rinp_m7.append(laygen.route(None, laygen.layers['metal'][7],
    #                     xy0=inp_xy_m6[0], xy1=[inp_xy_m6[0][0], inp_xy_m6[0][1]-14], gridname0=rg_m6m7_thick, via0=[0, 0]))
    #     rinm_m7.append(laygen.route(None, laygen.layers['metal'][7],
    #                        xy0=inm_xy_m6[1], xy1=[inm_xy_m6[1][0], inp_xy_m6[0][1]-14], gridname0=rg_m6m7_thick, via0=[0, 0]))
    #     inp_xy_m7 = laygen.get_rect_xy(rinp_m7[-1].name, rg_m7m8_thick)
    #     inm_xy_m7 = laygen.get_rect_xy(rinm_m7[-1].name, rg_m7m8_thick)
    #     for j in range(num_input_track):
    #         laygen.via(None, xy=inp_xy_m7[1] + [0, j], gridname=rg_m7m8_thick)
    #         laygen.via(None, xy=inm_xy_m7[1] + [0, j + num_input_track + 1], gridname=rg_m7m8_thick)
    # for j in range(num_input_track):
    #     rinp_m8 = laygen.route(None, laygen.layers['metal'][8], xy0=[3, inp_xy_m7[1][1]+j],
    #                            xy1=[laygen.grids.get_absgrid_x(rg_m7m8_thick, size_x)-3, inp_xy_m7[1][1]+j], gridname0=rg_m7m8_thick)
    #     rinm_m8 = laygen.route(None, laygen.layers['metal'][8], xy0=[3, inp_xy_m7[1][1] + j + num_input_track + 1],
    #                        xy1=[laygen.grids.get_absgrid_x(rg_m7m8_thick, size_x)-3, inp_xy_m7[1][1] + j + num_input_track + 1],
    #                        gridname0=rg_m7m8_thick)
    #     laygen.add_pin('INP'+str(j), layer=laygen.layers['pin'][8], xy=rinp_m8.xy, netname='INP')
    #     laygen.add_pin('INM' + str(j), layer=laygen.layers['pin'][8], xy=rinm_m8.xy, netname='INM')

    # ADC CAL
    rinp_m7=[]
    rinm_m7=[]
    isarcal_list = [isarcal0, isarcal1]
    for i in range(len(isarcal_list)):
        inp_xy0_m5 = pdict_m5m6_thick[isar.name]['INP%d' % (slice_order[num_slices-1])][1]
        inm_xy0_m5 = pdict_m5m6_thick[isar.name]['INM%d' % (slice_order[num_slices-1])][1]
        inp_xy_m5 = pdict_m5m6_thick[isarcal_list[i].name]['INP'][1]
        inm_xy_m5 = pdict_m5m6_thick[isarcal_list[i].name]['INM'][1]
        laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                         xy0=inp_xy0_m5, xy1=inp_xy_m5, track_y=inp_xy_m5[1] - 3,
                         gridname0=rg_m5m6_thick)
        laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][6],
                         xy0=inm_xy0_m5, xy1=inm_xy_m5, track_y=inm_xy_m5[1] - 2,
                         gridname0=rg_m5m6_thick)

    # for i in range(len(isarcal_list)):
    #     inp_xy_m5 = pdict_m5m6_thick[isarcal_list[i].name]['INP'][1]
    #     inm_xy_m5 = pdict_m5m6_thick[isarcal_list[i].name]['INM'][1]
    #     rinp_m6 = laygen.route(None, laygen.layers['metal'][6],
    #                     xy0=inp_xy_m5, xy1=inm_xy_m5, gridname0=rg_m5m6_thick, via0=[0,0])
    #     rinm_m6 = laygen.route(None, laygen.layers['metal'][6],
    #                        xy0=inp_xy_m5+[0,1], xy1=inm_xy_m5+[0,1], gridname0=rg_m5m6_thick, via1=[0, 0])
    #     inp_xy_m6 = laygen.get_rect_xy(rinp_m6.name, rg_m6m7_thick)
    #     inm_xy_m6 = laygen.get_rect_xy(rinm_m6.name, rg_m6m7_thick)
    #     rinp_m7.append(laygen.route(None, laygen.layers['metal'][7],
    #                     xy0=inp_xy_m6[0], xy1=[inp_xy_m6[0][0], inp_xy_m6[0][1]-14], gridname0=rg_m6m7_thick, via0=[0, 0]))
    #     rinm_m7.append(laygen.route(None, laygen.layers['metal'][7],
    #                        xy0=inm_xy_m6[1], xy1=[inm_xy_m6[1][0], inp_xy_m6[0][1]-14], gridname0=rg_m6m7_thick, via0=[0, 0]))
    #     inp_xy_m7 = laygen.get_rect_xy(rinp_m7[-1].name, rg_m7m8_thick)
    #     inm_xy_m7 = laygen.get_rect_xy(rinm_m7[-1].name, rg_m7m8_thick)
    #     for j in range(num_input_track):
    #         laygen.via(None, xy=inp_xy_m7[1] + [0, j], gridname=rg_m7m8_thick)
    #         laygen.via(None, xy=inm_xy_m7[1] + [0, j + num_input_track + 1], gridname=rg_m7m8_thick)

    # ADCCAL ofp/ofm route
    use_offset = False # To be done, not support True now
    if use_offset == True:
        for i in range(len(isarcal_list)):
            rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][3], layerh=laygen.layers['metal'][4],
                                     xy0=pdict_m3m4[i][isar.name]['OSP'][0],
                                     xy1=np.array([0, pdict_m3m4[i][isar.name]['OSP'][0][1] + 6 - (
                                     num_slices * 3) + 3 * slice_order[i]]),
                                     gridname0=rg_m3m4)
            # laygen.boundary_pin_from_rect(rh, rg_m3m4, 'OSP' + str(slice_order[i]), laygen.layers['pin'][4], size=8,
            #                               direction='left')
            rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][3], layerh=laygen.layers['metal'][4],
                                     xy0=pdict_m3m4[i][isar.name]['OSM'][0],
                                     xy1=np.array([0, pdict_m3m4[i][isar.name]['OSM'][0][1] + 6 - (
                                     num_slices * 3) + 3 * slice_order[i] + 1]),
                                     gridname0=rg_m3m4)
            # laygen.boundary_pin_from_rect(rh, rg_m3m4, 'OSM' + str(slice_order[i]), laygen.layers['pin'][4], size=8,
            #                               direction='left')
    else:
        for i in range(len(isarcal_list)):
            rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][3], layerh=laygen.layers['metal'][4],
                                     xy0=pdict_m3m4[isarcal_list[i].name]['OSP'][0],
                                     xy1=np.array(
                                         [0, pdict_m3m4[isarcal_list[i].name]['OSP'][0][1] + 0]), gridname0=rg_m3m4)
            rv, rh = laygen.route_vh(layerv=laygen.layers['metal'][3], layerh=laygen.layers['metal'][4],
                                     xy0=pdict_m3m4[isarcal_list[i].name]['OSM'][0],
                                     xy1=np.array(
                                         [0, pdict_m3m4[isarcal_list[i].name]['OSM'][0][1] + 0]), gridname0=rg_m3m4)
            rv0, rh1 = laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
                                       xy0=pdict_m4m5_basic_thick[isarcal_list[i].name]['VDDSAR0'][0] + [1, 0],
                                       xy1=np.array([0, pdict_m4m5_basic_thick[isarcal_list[i].name]['OSM'][0][1] + 0]),
                                       gridname0=rg_m4m5_basic_thick)

    # clock routing for ADC_CAL
    sarcal_clk_xy = []
    sarcal_clk_xy.append(pdict_m4m5_basic_thick[isarcal1.name]['CLK'][0])
    sarcal_clk_xy.append(pdict_m4m5_basic_thick[isarcal0.name]['CLK'][0])
    for i in range(2):
        # laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
        #                 xy0=sarcal_clk_xy[i],
        #                 xy1=pdict_m4m5_basic_thick[iclkcal.name]['CLKO<%d>'%(int(num_slices/2)+1-i)][0]-[3, 9],
        #                 track_y=sarcal_clk_xy[i][1]+3,
        #                 gridname0=rg_m4m5_basic_thick, layerv1=laygen.layers['metal'][5], extendl=0, extendr=0)
        # laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
        #              xy0=pdict_m4m5_basic_thick[iclkcal.name]['CLKO<%d>'%(int(num_slices/2)+1-i)][0]-[3, 9],
        #              xy1=pdict_m3m4[iclkcal.name]['CLKO<%d>'%(int(num_slices/2)+1-i)][0]-[0, 0],
        #              track_y=pdict_m4m5_basic_thick[iclkcal.name]['CLKO<%d>'%(int(num_slices/2)+1-i)][0][1]-9,
        #              gridname0=rg_m4m5_basic_thick, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4, extendl=0, extendr=0)
        x0 = sarcal_clk_xy[i][0]
        y1 = pdict_m4m5_basic_thick[iclkcal.name]['CLKO%d_0'%(int(num_slices/2)+1-i)][0][1]
        laygen.route_vh(layerv=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
                        xy0=pdict_m4m5[iclkcal.name]['CLKO%d_0'%(int(num_slices/2)+1-i)][0],
                        xy1=np.array([pdict_m4m5[isarcal_list[1-i].name]['CLK'][0][0], y1]), gridname0=rg_m4m5)
        laygen.route(None, layer=laygen.layers['metal'][5],
                     xy0=sarcal_clk_xy[i],
                     xy1=np.array([x0, y1 + 0]),
                     gridname0=rg_m4m5_basic_thick)
        laygen.via(None, np.array([x0, y1]), rg_m4m5_basic_thick)

    # ADC output to retimer
    for i in range(num_slices):
        for j in range(num_bits):
            ret_xy = pdict_m3m4[iret.name]['in_%d<%d>' % (i, j)][0]
            sar_xy = pdict_m4m5[isar.name]['ADCOUT%d<%d>' % (i, j)][0]
            laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
                     xy0=sar_xy, xy1=ret_xy,
                     track_y=sar_xy[1] + 1 - 1 * j,
                     gridname0=rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4, extendl=0, extendr=0)

    # ADC clock to retimer
    ck_phase_2 = num_slices - 1
    ck_phase_1 = int(num_slices / 2) - 1
    ck_phase_0_0 = int((int(num_slices / 2) + 1) % num_slices)
    ck_phase_0_1 = 1
    ck_phase_buf = sorted(set([ck_phase_2, ck_phase_1, ck_phase_0_0, ck_phase_0_1]))
    for i in range(len(ck_phase_buf)):
        sar_xy = pdict_m4m5[isar.name]['CLKO0%d' % (ck_phase_buf[i])][0]
        ret_xy = pdict_m3m4[iret.name]['clk%d' % (ck_phase_buf[i])][0]
        laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
                     xy0=sar_xy, xy1=ret_xy,
                     track_y=sar_xy[1]+3,
                     gridname0=rg_m4m5, layerv1=laygen.layers['metal'][3], gridname1=rg_m3m4, extendl=0, extendr=0)

    #RSTP route
    rstp_xy0 = pdict_m2m3[iclkdist.name]['RSTP'][0]
    rstp_xy1 = pdict_m2m3[iclkcal.name]['RSTP'][0]
    laygen.route_hvh(layerh0=laygen.layers['metal'][2], layerv=laygen.layers['metal'][3],
                     xy0=rstp_xy0, xy1=rstp_xy1, track_x=rstp_xy0[0]+3, gridname0=rg_m2m3)
    laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][3], #Bring RSTP to M4
                    xy0=laygen.get_inst_pin_xy(iclkdist.name, 'RSTP', rg_m3m4)[0]+np.array([6,2]),
                    xy1=laygen.get_inst_pin_xy(iclkdist.name, 'RSTP', rg_m3m4)[0]+np.array([3,0]), gridname0=rg_m3m4)
    laygen.via(None, laygen.get_inst_pin_xy(iclkdist.name, 'RSTP', rg_m2m3_pin)[0]+np.array([3,0]), rg_m2m3_pin)
    laygen.route_hvh(layerh0=laygen.layers['metal'][4], layerv=laygen.layers['metal'][5], layerh1=laygen.layers['metal'][6],
                     xy0=laygen.get_inst_pin_xy(iclkdist.name, 'RSTP', rg_m4m5)[0]+np.array([6,2]),
                     xy1=np.array([0, laygen.get_inst_pin_xy(irdac.name, 'out<0>', rg_m5m6)[0][1]-2]),
                     track_x=14, gridname0=rg_m4m5, gridname1=rg_m5m6) #Bring RSTP to RDAC boundary
    rh0, rrstp = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5], #Bring RSTP to digital boundary
                    xy0=np.array([0, laygen.get_inst_pin_xy(irdac.name, 'out<0>', rg_m5m6)[0][1]-2]),
                    xy1=np.array([laygen.get_inst_pin_xy(irdac.name, 'SEL<'+str(num_hori*num_vert*rdac_num_bits-1)+'>', rg_m5m6)[0][0]+2, 0]),
                    gridname0=rg_m5m6)

    laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][3], #Bring RSTN to M4
                    xy0=laygen.get_inst_pin_xy(iclkdist.name, 'RSTN', rg_m3m4)[0]+np.array([6,2]),
                    xy1=laygen.get_inst_pin_xy(iclkdist.name, 'RSTN', rg_m3m4)[0]+np.array([1,0]), gridname0=rg_m3m4)
    laygen.via(None, laygen.get_inst_pin_xy(iclkdist.name, 'RSTN', rg_m2m3_pin)[0]+np.array([1,0]), rg_m2m3_pin)
    laygen.route_hvh(layerh0=laygen.layers['metal'][4], layerv=laygen.layers['metal'][5], layerh1=laygen.layers['metal'][6],
                     xy0=laygen.get_inst_pin_xy(iclkdist.name, 'RSTN', rg_m4m5)[0]+np.array([6,2]),
                     xy1=np.array([0, laygen.get_inst_pin_xy(irdac.name, 'out<0>', rg_m5m6)[0][1]-3]),
                     track_x=15, gridname0=rg_m4m5, gridname1=rg_m5m6) #Bring RSTN to RDAC boundary
    rh0, rrstn = laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5], #Bring RSTN to digital boundary
                    xy0=np.array([0, laygen.get_inst_pin_xy(irdac.name, 'out<0>', rg_m5m6)[0][1]-3]),
                    xy1=np.array([laygen.get_inst_pin_xy(irdac.name, 'SEL<'+str(num_hori*num_vert*rdac_num_bits-1)+'>', rg_m5m6)[0][0]+3, 0]),
                    gridname0=rg_m5m6)
    # laygen.pin('RSTP', layer=laygen.layers['pin'][2], xy=laygen.get_inst_pin_xy(iclkdist.name, 'RSTP', rg_m2m3_pin), gridname=rg_m2m3_pin)
    # laygen.pin('RSTN', layer=laygen.layers['pin'][2], xy=laygen.get_inst_pin_xy(iclkdist.name, 'RSTN', rg_m2m3_pin), gridname=rg_m2m3_pin)
    laygen.boundary_pin_from_rect(rrstp, rg_m5m6, 'RSTP', layer=laygen.layers['pin'][5], direction='bottom', size=4)
    laygen.boundary_pin_from_rect(rrstn, rg_m5m6, 'RSTN', layer=laygen.layers['pin'][5], direction='bottom', size=4)

    # SF_bypass route
    bypass_sar = pdict_m4m5[isar.name]['SF_bypass'][0]
    bypass_sarcal0 = pdict_m4m5[isarcal0.name]['SF_bypass'][0]
    bypass_sarcal1 = pdict_m4m5[isarcal1.name]['SF_bypass'][0]
    r0 = laygen.route(None, laygen.layers['metal'][4],
                      xy0=bypass_sar, xy1=bypass_sarcal0,
                      gridname0=rg_m4m5)
    rh0, rbyp = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                    xy0=bypass_sar,
                    xy1=np.array([laygen.get_inst_pin_xy(irdac.name, 'SEL<'+str(num_hori*num_vert*rdac_num_bits-1)+'>', rg_m4m5)[0][0]+4, 0]),
                    gridname0=rg_m4m5)
    laygen.boundary_pin_from_rect(rbyp, rg_m4m5, 'SF_bypass', layer=laygen.layers['pin'][5], direction='bottom', size=4)

    # VREF_SF_bypass route
    bypass_sar = pdict_m4m5[isar.name]['VREF_SF_bypass'][0]
    rh0, rbyp = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                    xy0=bypass_sar,
                    xy1=np.array([bypass_sar[0], 0]),
                    gridname0=rg_m4m5)
    laygen.boundary_pin_from_rect(rbyp, rg_m4m5, 'VREF_SF_bypass', layer=laygen.layers['pin'][5], direction='bottom', size=4)

    # RDAC routing
    for i in range(num_slices):
        laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                        xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(i) + '>', rg_m5m6_thick_basic)[0],
                        xy1=laygen.get_inst_pin_xy(isar.name, 'SF_Voffp' + str(i), rg_m5m6_thick_basic)[0],
                        gridname0=rg_m5m6_thick_basic)
        laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                        xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices+i) + '>', rg_m5m6_thick_basic)[0],
                        xy1=laygen.get_inst_pin_xy(isar.name, 'SF_Voffn' + str(i), rg_m5m6_thick_basic)[0],
                        gridname0=rg_m5m6_thick_basic)
        # laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
        #                 xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices*3) + '>', rg_m5m6_thick_basic)[0],
        #                 xy1=laygen.get_inst_pin_xy(isar.name, 'SF_BIAS' + str(i), rg_m5m6_thick_basic)[0],

        laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                        xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices*2+i) + '>', rg_m5m6_thick_basic)[0],
                        xy1=np.array([laygen.get_inst_pin_xy(isar.name, 'SF_Voffp' + str(i), rg_m5m6_thick_basic)[0][0]-1,
                                      laygen.get_inst_pin_xy(isar.name, 'samp_body' + str(i)+'_M6', rg_m5m6_thick_basic)[0][1]]),
                        gridname0=rg_m5m6_thick_basic, gridname1=rg_m5m6_thick_basic)
        laygen.via(None,np.array([laygen.get_inst_pin_xy(isar.name, 'SF_Voffp' + str(i), rg_m5m6_thick)[0][0]-1,
                                  laygen.get_inst_pin_xy(isar.name, 'samp_body' + str(i)+'_M6', rg_m5m6_thick)[0][1]]), rg_m5m6_thick)
        # x_mid = laygen.get_inst_pin_xy(isar.name, 'INP' + str(i), rg_m6m7_basic_thick)[0][0]/2 + \
        #         laygen.get_inst_pin_xy(isar.name, 'INM' + str(i), rg_m6m7_basic_thick)[0][0]/2
        # laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][7],
        #                 xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices * 3 + 1) + '>', rg_m6m7_basic_thick)[0],
        #                 xy1=np.array([x_mid, laygen.get_inst_pin_xy(isar.name, 'VREF_SF_BIAS' + str(i), rg_m6m7_basic_thick)[0][1]]),
        #                 gridname0=rg_m6m7_basic_thick)
        # laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][7],
        #                 xy0=laygen.get_inst_pin_xy(isar.name, 'VREF_SF_BIAS' + str(i), rg_m5m6_thick)[0],
        #                 xy1=np.array([x_mid, laygen.get_inst_pin_xy(isar.name, 'VREF_SF_BIAS' + str(i), rg_m6m7_basic_thick)[0][1]]),
        #                 gridname0=rg_m6m7_basic_thick, gridname1=rg_m6m7_basic_thick)
        laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                        xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_vert*num_hori-1) + '>', rg_m5m6_thick)[0],
                        xy1=laygen.get_inst_pin_xy(isar.name, 'VREF_SF_BIAS' + str(i), rg_m5m6_thick)[0],
                        gridname0=rg_m5m6_thick)
        # laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
        #                 xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices * 2 + 1) + '>', rg_m5m6_thick_basic)[0],
        #                 xy1=laygen.get_inst_pin_xy(isar.name, 'VREF_SF_BIAS' + str(i), rg_m5m6_thick_basic)[0],
        #                 gridname0=rg_m5m6_thick_basic)
    laygen.route(None, laygen.layers['metal'][6],
                 xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices * 3) + '>', rg_m5m6_thick)[0],
                 xy1=laygen.get_inst_pin_xy(isarcal0.name, 'SF_BIAS', rg_m5m6_thick)[0],
                 gridname0=rg_m5m6_thick) # connect all SF_BIAS
    # laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
    #                 xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices * 2) + '>', rg_m5m6_thick_basic)[0],
    #                 xy1=laygen.get_inst_pin_xy(isarcal0.name, 'SF_BIAS', rg_m5m6_thick_basic)[0],
    #                 gridname0=rg_m5m6_thick_basic)
    laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                    xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_vert*num_hori-1) + '>', rg_m5m6_thick)[0],
                    xy1=laygen.get_inst_pin_xy(isarcal0.name, 'VREF_SF_BIAS', rg_m5m6_thick)[0],
                    gridname0=rg_m5m6_thick)
    laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                    xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices*3 + 2) + '>', rg_m5m6_thick_basic)[0],
                    xy1=laygen.get_inst_pin_xy(isarcal0.name, 'SF_Voffp', rg_m5m6_thick_basic)[0],
                    gridname0=rg_m5m6_thick_basic)
    laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                    xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices*3 + 3) + '>', rg_m5m6_thick_basic)[0],
                    xy1=laygen.get_inst_pin_xy(isarcal0.name, 'SF_Voffn', rg_m5m6_thick_basic)[0],
                    gridname0=rg_m5m6_thick_basic)
    # laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
    #                 xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices * 2) + '>', rg_m5m6_thick_basic)[0],
    #                 xy1=laygen.get_inst_pin_xy(isarcal1.name, 'SF_BIAS', rg_m5m6_thick_basic)[0],
    #                 gridname0=rg_m5m6_thick_basic)
    laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                    xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_vert*num_hori-1) + '>', rg_m5m6_thick)[0],
                    xy1=laygen.get_inst_pin_xy(isarcal1.name, 'VREF_SF_BIAS', rg_m5m6_thick)[0],
                    gridname0=rg_m5m6_thick)
    laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                    xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices*3 + 4) + '>', rg_m5m6_thick_basic)[0],
                    xy1=laygen.get_inst_pin_xy(isarcal1.name, 'SF_Voffp', rg_m5m6_thick_basic)[0],
                    gridname0=rg_m5m6_thick_basic)
    laygen.route_hv(laygen.layers['metal'][6], laygen.layers['metal'][5],
                    xy0=laygen.get_inst_pin_xy(irdac.name, 'out<' + str(num_slices*3 + 5) + '>', rg_m5m6_thick_basic)[0],
                    xy1=laygen.get_inst_pin_xy(isarcal1.name, 'SF_Voffn', rg_m5m6_thick_basic)[0],
                    gridname0=rg_m5m6_thick_basic)

    # Retimer pins
    for i in range(num_slices):
        for j in range(num_bits):
            pxy = laygen.get_inst_pin_xy(iret.name, 'out_%d<%d>'%(i,j), rg_m3m4)
            laygen.pin('ADCOUT_RET%d<%d>'%(i,j), layer=laygen.layers['pin'][3], xy=pxy, gridname=rg_m3m4)
    pxy = laygen.get_inst_pin_xy(iret.name, 'ck_out', rg_m4m5)
    laygen.pin('CLKOUT_DES', layer=laygen.layers['pin'][5], xy=pxy, gridname=rg_m4m5)

    # TIADC pins
    sar_template = laygen.templates.get_template(sar_name, sar_libname)
    sar_pins = sar_template.pins
    for i in range(num_slices):
        for j in range(num_bits):
            pxy = laygen.get_inst_pin_xy(isar.name, 'ADCOUT%d<%d>'%(i,j), rg_m4m5)
            rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
            laygen.boundary_pin_from_rect(rout, rg_m4m5, 'ADCO%d<%d>'%(i,j), layer=laygen.layers['pin'][5], direction='bottom', size=4)
        pxy = laygen.get_inst_pin_xy(isar.name, 'CLKO0%d' % (i), rg_m4m5)
        refxy = laygen.get_inst_pin_xy(isar.name, 'ADCOUT%d<0>'%(i), rg_m4m5)
        rv0, rh0, rout = laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
            xy0=pxy[0], xy1=[refxy[0][0]-3, 0], track_y=pxy[0][1]+2, gridname0=rg_m4m5)
        laygen.boundary_pin_from_rect(rout, rg_m4m5, 'CLKO%d' % (i), layer=laygen.layers['pin'][5], direction='bottom', size=4)
    for pn, p in sar_pins.items():
        if pn.startswith('ASCLKD'):
            pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m4m5)
            rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
            laygen.boundary_pin_from_rect(rout, rg_m4m5, pn, layer=laygen.layers['pin'][5],
                                      direction='bottom', size=4)
        if pn.startswith('EXTSEL_'):
            pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m4m5)
            rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
            laygen.boundary_pin_from_rect(rout, rg_m4m5, pn, layer=laygen.layers['pin'][5],
                                      direction='bottom', size=4)
        if pn.startswith('VREF<'):
            pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m5m6_thick)
            laygen.pin(pn, layer=sar_pins[pn]['layer'], xy=pxy, gridname=rg_m5m6_thick, netname=pn.split("_")[0])
        # if pn.startswith('samp_body'):
        #     pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m5m6_thick)
        #     laygen.pin(pn, layer=sar_pins[pn]['layer'], xy=pxy, gridname=rg_m5m6_thick)
        # if pn.startswith('bottom_body'):
        #     pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m3m4)
        #     laygen.pin(pn, layer=sar_pins[pn]['layer'], xy=pxy, gridname=rg_m3m4, netname=pn.split("_bottom")[0])

    # CAL ADC pins
    sar_template = laygen.templates.get_template(sar_slice_name, sar_libname)
    sar_pins = sar_template.pins
    isarcal_name = [isarcal0.name, isarcal1.name]
    for i in range(len(isarcal_name)):
        for j in range(num_bits):
            pxy = laygen.get_inst_pin_xy(isarcal_name[i], 'ADCOUT<%d>' % (j), rg_m4m5)
            rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
            laygen.boundary_pin_from_rect(rout, rg_m4m5, 'ADCO_CAL%d<%d>' % (i, j), layer=laygen.layers['pin'][5],
                                          direction='bottom', size=4)
        pxy = laygen.get_inst_pin_xy(isarcal_name[i], 'CLKO0', rg_m4m5)
        refxy = laygen.get_inst_pin_xy(isarcal_name[i], 'ADCOUT<0>', rg_m4m5)
        rv0, rh0, rout = laygen.route_vhv(layerv0=laygen.layers['metal'][5], layerh=laygen.layers['metal'][4],
                                          xy0=pxy[0], xy1=[refxy[0][0] - 3, 0], track_y=pxy[0][1]+2, gridname0=rg_m4m5)
        laygen.boundary_pin_from_rect(rout, rg_m4m5, 'CLKO_CAL%d' % (i), layer=laygen.layers['pin'][5],
                                      direction='bottom', size=4)
        ckd_pin_list = ['CKDSEL1<1>', 'CKDSEL1<0>', 'CKDSEL0<1>', 'CKDSEL0<0>', 'EXTSEL_CLK']
        for j in range(len(ckd_pin_list)):
            pxy = laygen.get_inst_pin_xy(isarcal_name[i], ckd_pin_list[j], rg_m4m5)
            rout = laygen.route(None, laygen.layers['metal'][5], pxy[0], [pxy[0][0], 0], rg_m4m5)
            if j < 4:
                laygen.boundary_pin_from_rect(rout, rg_m4m5, 'ASCLKD_CAL%d<%d>'%(i, 3-j), layer=laygen.layers['pin'][5],
                                          direction='bottom', size=4)
            else:
                laygen.boundary_pin_from_rect(rout, rg_m4m5, 'EXTSEL_CLK_CAL%d'%(i), layer=laygen.layers['pin'][5],
                                          direction='bottom', size=4)
        # for pn, p in sar_pins.items():
            # if pn.startswith('samp_body'):
            #     pxy = laygen.get_inst_pin_xy(isarcal_name[i], pn, rg_m5m6_thick)
            #     laygen.pin(pn+str(num_slices+1-i), layer=sar_pins[pn]['layer'], xy=pxy, gridname=rg_m5m6_thick)
            # if pn.startswith('bottom_body'):
            #     pxy = laygen.get_inst_pin_xy(isarcal_name[i], pn, rg_m3m4)
            #     laygen.pin(pn+str(num_slices+1-i), layer=sar_pins[pn]['layer'], xy=pxy, gridname=rg_m3m4, netname='bottom_body%d'%(num_slices+1-i))

    # CLKDIST pins
    clkdist_template = laygen.templates.get_template(clkdist_name, clkdist_libname)
    clkdist_pins = clkdist_template.pins
    for pn, p in clkdist_pins.items():
        if pn.startswith('CLKCAL'):
            pxy=laygen.get_inst_pin_xy(iclkdist.name, pn, rg_m2m3_pin)
            laygen.pin(pn, layer=clkdist_pins[pn]['layer'], xy=pxy, gridname=rg_m2m3_pin)

    # Bottom plate body bias pins
    sar_template = laygen.templates.get_template(sar_name, sar_libname)
    sar_pins = sar_template.pins
    y0_m6m7 = laygen.grids.get_absgrid_y(rg_m6m7_thick, size_y)
    if not num_inv_bb == 0:
        for i in range(num_slices):
            for pn, p in sar_pins.items():
                if pn.startswith('bottom_body'+str(i)+'_'):
                    pxy = laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
                    r_m7 = laygen.route(None, laygen.layers['metal'][7], pxy[1], [pxy[1][0], y0_m6m7], rg_m6m7_thick)
                    laygen.boundary_pin_from_rect(r_m7, rg_m6m7_thick, 'bottom_body'+str(i), laygen.layers['pin'][7], size=6, direction='top')
        sar_template = laygen.templates.get_template(sar_slice_name, sar_libname)
        sar_pins = sar_template.pins
        for i in range(len(isarcal_name)):
            for pn, p in sar_pins.items():
                if pn.startswith('bottom_body'):
                    pxy = laygen.get_inst_pin_xy(isarcal_name[i], pn, rg_m6m7_thick)
                    r_m7 = laygen.route(None, laygen.layers['metal'][7], pxy[1], [pxy[1][0], y0_m6m7], rg_m6m7_thick)
                    laygen.boundary_pin_from_rect(r_m7, rg_m6m7_thick, 'bottom_body' + str(num_slices+1-i), laygen.layers['pin'][7], size=6,
                                              direction='top')
    # # Top plate body bias pins
    # sar_template = laygen.templates.get_template(sar_name, sar_libname)
    # sar_pins = sar_template.pins
    # for i in range(num_slices):
    #     for pn, p in sar_pins.items():
    #         if pn.startswith('samp_body'+str(i)+'_'):
    #             pxy = laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
    #             r_m7 = laygen.route(None, laygen.layers['metal'][7], pxy[1]-[1,0], [pxy[1][0]-1, y0_m6m7], rg_m6m7_thick, via0=[0, 0])
    #             laygen.boundary_pin_from_rect(r_m7, rg_m6m7_thick, 'samp_body'+str(i), laygen.layers['pin'][7], size=6, direction='top')
    # sar_template = laygen.templates.get_template(sar_slice_name, sar_libname)
    # sar_pins = sar_template.pins
    # for i in range(len(isarcal_name)):
    #     for pn, p in sar_pins.items():
    #         if pn.startswith('samp_body'):
    #             pxy = laygen.get_inst_pin_xy(isarcal_name[i], pn, rg_m6m7_thick)
    #             r_m7 = laygen.route(None, laygen.layers['metal'][7], pxy[1]-[1,0], [pxy[1][0]-1, y0_m6m7], rg_m6m7_thick, via0=[0, 0])
    #             laygen.boundary_pin_from_rect(r_m7, rg_m6m7_thick, 'samp_body' + str(num_slices + 1 - i),
    #                                           laygen.layers['pin'][7], size=6,
    #                                           direction='top')

    # RDAC control pins
    rdac_template = laygen.templates.get_template(rdac_name, rdac_libname)
    rdac_pins = rdac_template.pins
    for pn, p in rdac_pins.items():
        if pn.startswith('SEL<'):
            pxy = laygen.get_inst_pin_xy(irdac.name, pn, rg_m5m6)
            laygen.pin('RDAC_'+pn, layer=rdac_pins[pn]['layer'], xy=pxy, gridname=rg_m5m6)

    # VDD/VSS connection for retimer
    ret_template = laygen.templates.get_template(ret_name, ret_libname)
    ret_pins = ret_template.pins
    for pn, p in ret_pins.items():
        if pn.startswith('VDD'):
            pxy=laygen.get_inst_pin_xy(iret.name, pn, rg_m5m6_thick)
            laygen.route(None, laygen.layers['metal'][5], pxy[1], pxy[1]+[0, 10], rg_m5m6_thick)
        if pn.startswith('VSS'):
            pxy=laygen.get_inst_pin_xy(iret.name, pn, rg_m5m6_thick)
            laygen.route(None, laygen.layers['metal'][5], pxy[1], pxy[1]+[0, 10], rg_m5m6_thick)

    # VDD/VSS rails in M7
    rvdd_m6_bot=[]
    rvss_m6_bot=[]
    rvdd_m6_top=[]
    rvss_m6_top=[]
    sar_template = laygen.templates.get_template(sar_name, sar_libname)
    sar_pins = sar_template.pins
    x0_m6m7 = laygen.grids.get_absgrid_x(rg_m6m7_thick, size_x)
    y0_m6m7 = laygen.grids.get_absgrid_y(rg_m6m7_thick, size_y)
    for pn, p in sar_pins.items():
        if pn.startswith('VDDSAR'):
            pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
            rvdd_m6_bot.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
        if pn.startswith('VSSSAR'):
            pxy=laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
            rvss_m6_bot.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
        if pn.startswith('VDDSAMP'):
            pxy = laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
            rvdd_m6_top.append(
                laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
        if pn.startswith('VSSSAMP'):
            pxy = laygen.get_inst_pin_xy(isar.name, pn, rg_m6m7_thick)
            rvss_m6_top.append(
                laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
    clkdist_template = laygen.templates.get_template(clkdist_name, clkdist_libname)
    clkdist_pins = clkdist_template.pins
    for pn, p in clkdist_pins.items():
        if pn.startswith('VDD'):
            pxy = laygen.get_inst_pin_xy(iclkdist.name, pn, rg_m6m7_thick)
            rvdd_m6_top.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
        if pn.startswith('VSS'):
            pxy = laygen.get_inst_pin_xy(iclkdist.name, pn, rg_m6m7_thick)
            rvss_m6_top.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
    clkcal_template = laygen.templates.get_template(clkcal_name, clkdist_libname)
    clkcal_pins = clkcal_template.pins
    for pn, p in clkcal_pins.items():
        if pn.startswith('VDD'):
            pxy = laygen.get_inst_pin_xy(iclkcal.name, pn, rg_m6m7_thick)
            rvdd_m6_top.append(laygen.route(None, laygen.layers['metal'][6], [0, pxy[0][1]], pxy[1], rg_m6m7_thick))
        if pn.startswith('VSS'):
            pxy = laygen.get_inst_pin_xy(iclkcal.name, pn, rg_m6m7_thick)
            rvss_m6_top.append(laygen.route(None, laygen.layers['metal'][6], [0, pxy[0][1]], pxy[1], rg_m6m7_thick))
    dcap_template = laygen.templates.get_template('tisaradc_dcap_array', sar_libname)
    dcap_pins = dcap_template.pins
    for pn, p in dcap_pins.items():
        if pn.startswith('VDD'):
            pxy = laygen.get_inst_pin_xy(idcap.name, pn, rg_m6m7_thick)
            rvdd_m6_top.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], pxy[1], rg_m6m7_thick))
        if pn.startswith('VSS'):
            pxy = laygen.get_inst_pin_xy(idcap.name, pn, rg_m6m7_thick)
            rvss_m6_top.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], pxy[1], rg_m6m7_thick))

    w_size = laygen.get_template_size(sar_slice_name, rg_m6m7_thick, libname=sar_libname)[0]
    # if not num_inv_bb==0:
    #     botbody_x = laygen.get_template_pin_xy(sar_slice_name, 'bottom_body_M7_0', rg_m6m7_thick, libname=workinglib)[0][0]
    # else:
    #     botbody_x = laygen.get_template_pin_xy(sar_slice_name, 'samp_body', rg_m6m7_thick, libname=workinglib)[1][0]
    botbody_x = laygen.get_inst_pin_xy(ihtree_in.name, 'WPO_0_0', rg_m6m7_thick)[0][0]

    # for i in range(2):
    # end_coord = None
    end_coord = laygen.get_inst_pin_xy(isar.name, 'VDDSAMP0', rg_m6m7_thick)[0][1]
    # end_coord = laygen.get_inst_xy(idcap.name, gridname=rg_m6m7_thick)[1]+laygen.get_template_size('tisaradc_dcap_array', gridname=rg_m6m7_thick, libname=workinglib)[1]
    for i in range(num_slices+2):
        rvdd_m7_0, rvss_m7_0 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M7_0_'+str(i),
                                                                           layer=laygen.layers['pin'][7],
                                                                           gridname=rg_m6m7_thick,
                                                                           netnames=['VDD:', 'VSS:'], direction='y',
                                                                           input_rails_rect=[rvdd_m6_bot, rvss_m6_bot],
                                                                           generate_pin=True,
                                                                           overwrite_start_coord=0,
                                                                           overwrite_end_coord=end_coord,
                                                                           overwrite_num_routes=None,
                                                                           overwrite_start_index=w_size*i,
                                                                           overwrite_end_index=w_size*i+botbody_x-2)
    # rvdd_m7_1, rvss_m7_1 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M7_1',
    #                                                                        layer=laygen.layers['pin'][7],
    #                                                                        gridname=rg_m6m7_thick,
    #                                                                        netnames=['VDD:', 'VSS:'], direction='y',
    #                                                                        input_rails_rect=[rvdd_m6_bot, rvss_m6_bot],
    #                                                                        generate_pin=True,
    #                                                                        overwrite_start_coord=0,
    #                                                                        overwrite_end_coord=None,
    #                                                                        overwrite_num_routes=50,
    #                                                                        offset_start_index=200,
    #                                                                        offset_end_index=0)
    # rvdd_m7_2, rvss_m7_2 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M7_2',
    #                                                                        layer=laygen.layers['pin'][7],
    #                                                                        gridname=rg_m6m7_thick,
    #                                                                        netnames=['VDD:', 'VSS:'], direction='y',
    #                                                                        input_rails_rect=[rvdd_m6_bot, rvss_m6_bot],
    #                                                                        generate_pin=True,
    #                                                                        overwrite_start_coord=0,
    #                                                                        overwrite_end_coord=None,
    #                                                                        overwrite_num_routes=50,
    #                                                                        offset_start_index=800,
    #                                                                        offset_end_index=0)
    # rvdd_m7_3, rvss_m7_3 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M7_3',
    #                                                                        layer=laygen.layers['pin'][7],
    #                                                                        gridname=rg_m6m7_thick,
    #                                                                        netnames=['VDD:', 'VSS:'], direction='y',
    #                                                                        input_rails_rect=[rvdd_m6_bot, rvss_m6_bot],
    #                                                                        generate_pin=True,
    #                                                                        overwrite_start_coord=0,
    #                                                                        overwrite_end_coord=None,
    #                                                                        overwrite_num_routes=None,
    #                                                                        offset_start_index=1000,
    #                                                                        offset_end_index=-2)

        rvdd_m7_6, rvss_m7_6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M7_6_'+str(i),
                                                                             layer=laygen.layers['pin'][7],
                                                                             gridname=rg_m6m7_thick,
                                                                             netnames=['VDD:', 'VSS:'], direction='y',
                                                                             input_rails_rect=[rvdd_m6_top,
                                                                                               rvss_m6_top],
                                                                             generate_pin=True,
                                                                             overwrite_start_coord=None,
                                                                             # overwrite_end_coord=y0_m6m7,
                                                                             overwrite_end_coord=None,
                                                                             overwrite_num_routes=None,
                                                                             overwrite_start_index=w_size * i,
                                                                             overwrite_end_index=w_size * i + botbody_x - 2)
    # rvdd_m7_7, rvss_m7_7 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M7_7',
    #                                                                          layer=laygen.layers['pin'][7],
    #                                                                          gridname=rg_m6m7_thick,
    #                                                                          netnames=['VDD:', 'VSS:'], direction='y',
    #                                                                          input_rails_rect=[rvdd_m6_top,
    #                                                                                            rvss_m6_top],
    #                                                                          generate_pin=True,
    #                                                                          overwrite_start_coord=None,
    #                                                                          overwrite_end_coord=y0_m6m7,
    #                                                                          overwrite_num_routes=50,
    #                                                                          offset_start_index=200,
    #                                                                          offset_end_index=0)
    # rvdd_m7_8, rvss_m7_8 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M7_8',
    #                                                                          layer=laygen.layers['pin'][7],
    #                                                                          gridname=rg_m6m7_thick,
    #                                                                          netnames=['VDD:', 'VSS:'], direction='y',
    #                                                                          input_rails_rect=[rvdd_m6_top,
    #                                                                                            rvss_m6_top],
    #                                                                          generate_pin=True,
    #                                                                          overwrite_start_coord=None,
    #                                                                          overwrite_end_coord=y0_m6m7,
    #                                                                          overwrite_num_routes=50,
    #                                                                          offset_start_index=800,
    #                                                                          offset_end_index=0)
    # rvdd_m7_9, rvss_m7_9 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M7_9',
    #                                                                          layer=laygen.layers['pin'][7],
    #                                                                          gridname=rg_m6m7_thick,
    #                                                                          netnames=['VDD:', 'VSS:'], direction='y',
    #                                                                          input_rails_rect=[rvdd_m6_top,
    #                                                                                            rvss_m6_top],
    #                                                                          generate_pin=True,
    #                                                                          overwrite_start_coord=None,
    #                                                                          overwrite_end_coord=y0_m6m7,
    #                                                                          overwrite_num_routes=None,
    #                                                                          offset_start_index=1000,
    #                                                                          offset_end_index=0)
    #
    # #input pins
    # #make virtual grids and route on the grids (assuming drc clearance of each block)
    # rg_m5m6_thick_temp_sig='route_M5_M6_thick_temp_sig'
    # laygenhelper.generate_grids_from_inst(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_sig,
    #                                       instname=isar.name,
    #                                       inst_pin_prefix=['INP', 'INM'], xy_grid_type='xgrid')
    # pdict_m5m6_thick_temp_sig = laygen.get_inst_pin_coord(None, None, rg_m5m6_thick_temp_sig)
    # inp_x_list=[]
    # inm_x_list=[]
    # num_input_track=4
    # in_x0 = pdict_m5m6_thick_temp_sig[isar.name]['INP0'][0][0]
    # in_x1 = pdict_m5m6_thick_temp_sig[isar.name]['INM0'][0][0]
    # in_y0 = pdict_m5m6_thick_temp_sig[isar.name]['INP0'][1][1]
    # in_y1 = in_y0+6
    # in_y2 = in_y1+2*num_input_track
    # for i in range(num_slices):
    #     in_x0 = min(in_x0, pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0])
    #     in_x1 = max(in_x1, pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0])
    #     laygen.route(None, laygen.layers['metal'][5],
    #                  xy0=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0], in_y0]),
    #                  xy1=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0], in_y2]),
    #                  gridname0=rg_m5m6_thick_temp_sig)
    #     laygen.route(None, laygen.layers['metal'][5],
    #                  xy0=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0], in_y0]),
    #                  xy1=np.array([pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0], in_y2]),
    #                  gridname0=rg_m5m6_thick_temp_sig)
    #     for j in range(num_input_track):
    #         laygen.via(None,np.array([pdict_m5m6_thick_temp_sig[isar.name]['INP'+str(i)][0][0], in_y1+2*j]), rg_m5m6_thick_temp_sig)
    #         laygen.via(None,np.array([pdict_m5m6_thick_temp_sig[isar.name]['INM'+str(i)][0][0], in_y1+2*j+1]), rg_m5m6_thick_temp_sig)
    # #in_x0 -= 2
    # #in_x1 += 2
    # rinp=[]
    # rinm=[]
    # for i in range(num_input_track):
    #     rinp.append(laygen.route(None, laygen.layers['metal'][6], xy0=np.array([in_x0, in_y1+2*i]), xy1=np.array([in_x1, in_y1+2*i]), gridname0=rg_m5m6_thick_temp_sig))
    #     rinm.append(laygen.route(None, laygen.layers['metal'][6], xy0=np.array([in_x0, in_y1+2*i+1]), xy1=np.array([in_x1, in_y1+2*i+1]), gridname0=rg_m5m6_thick_temp_sig))
    #     laygen.add_pin('INP' + str(i), 'INP', rinp[-1].xy, laygen.layers['pin'][6])
    #     laygen.add_pin('INM' + str(i), 'INM', rinm[-1].xy, laygen.layers['pin'][6])
    #

    # VDD/VSS rails in M7 for RDAC
    rvdd_m6_rdac=[]
    rvss_m6_rdac=[]
    rdac_template = laygen.templates.get_template(rdac_name, rdac_libname)
    rdac_pins = rdac_template.pins
    x0_m6m7 = -laygen.grids.get_absgrid_x(rg_m6m7_thick, irdac.size[0])
    y0_m6m7 = laygen.grids.get_absgrid_y(rg_m6m7_thick, irdac.size[1])
    for pn, p in rdac_pins.items():
        if pn.startswith('VDD'):
            pxy=laygen.get_inst_pin_xy(irdac.name, pn, rg_m6m7_thick)
            rvdd_m6_rdac.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
        if pn.startswith('VSS'):
            pxy=laygen.get_inst_pin_xy(irdac.name, pn, rg_m6m7_thick)
            rvss_m6_rdac.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], [x0_m6m7, pxy[1][1]], rg_m6m7_thick))
    dcap_template = laygen.templates.get_template('tisaradc_dcap_array', sar_libname)
    dcap_pins = dcap_template.pins
    for pn, p in dcap_pins.items():
        if pn.startswith('VDD'):
            pxy = laygen.get_inst_pin_xy(idcap.name, pn, rg_m6m7_thick)
            rvdd_m6_rdac.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], pxy[1], rg_m6m7_thick))
        if pn.startswith('VSS'):
            pxy = laygen.get_inst_pin_xy(idcap.name, pn, rg_m6m7_thick)
            rvss_m6_rdac.append(laygen.route(None, laygen.layers['metal'][6], pxy[0], pxy[1], rg_m6m7_thick))
    rvdd_m7_rdac, rvss_m7_rdac = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='M7_RDAC_',
                                                                           layer=laygen.layers['pin'][7],
                                                                           gridname=rg_m6m7_thick,
                                                                           netnames=['VDD:', 'VSS:'], direction='y',
                                                                           input_rails_rect=[rvdd_m6_rdac, rvss_m6_rdac],
                                                                           generate_pin=True,
                                                                           overwrite_start_coord=None,
                                                                           overwrite_end_coord=None,
                                                                           overwrite_num_routes=None,
                                                                           overwrite_start_index=x0_m6m7+2,
                                                                           # overwrite_end_index=x0_m6m7+4)
                                                                           overwrite_end_index=-2)

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
    ret_libname = 'adc_sar_generated'
    clkdist_libname = 'clk_dis_generated'
    laygen.load_template(filename=tech+'_microtemplates_dense_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=tech+'_microtemplates_dense_grids.yaml', libname=utemplib)
    laygen.load_template(filename=logictemplib+'.yaml', libname=logictemplib)
    # laygen.load_template(filename='adc_retimer.yaml', libname=ret_libname)
    #laygen.load_template(filename=ret_libname+'.yaml', libname=ret_libname)
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
    rg_m5m6_basic_thick = 'route_M5_M6_basic_thick'
    rg_m5m6_thick_basic = 'route_M5_M6_thick_basic'
    rg_m5m6_thick2_thick = 'route_M5_M6_thick2_thick'
    rg_m6m7_thick = 'route_M6_M7_thick'
    rg_m6m7_basic_thick = 'route_M6_M7_basic_thick'
    rg_m6m7_thick2_thick = 'route_M6_M7_thick2_thick'
    rg_m7m8_thick = 'route_M7_M8_thick'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    num_bits=9
    num_slices=9
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
        num_inv_bb=sizedict['sarlogic']['num_inv_bb']
        rdac_num_bits=sizedict['r2rdac']['num_bits']
        num_hori=sizedict['r2rdac_array']['num_hori']
        num_vert=sizedict['r2rdac_array']['num_vert']
        trackm=sizedict['clk_dis_htree']['m_track']
        slice_order=sizedict['slice_order']
        clk_pulse=specdict['clk_pulse_overlap']

    cellname = 'tisaradc_splash'
    sar_name = 'sar_wsamp_bb_doubleSA_array'
    sar_slice_name = 'sar_wsamp_bb_doubleSA'
    ret_name = 'adc_retimer'
    clkdist_name = 'clk_dis_viadel_htree'
    clkcal_name = 'clk_dis_viadel_cal'
    rdac_name = 'r2r_dac_array'
    htree_name = 'tisar_htree_diff'
    #tisar_space_name = 'tisaradc_body_space'
    space_1x_name = 'space_1x'
     

    #sar generation
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_tisaradc_splash(laygen, objectname_pfix='TISAR0',
                 ret_libname=ret_libname, sar_libname=workinglib, clkdist_libname=clkdist_libname, rdac_libname=workinglib, space_1x_libname=logictemplib,
                 ret_name=ret_name, sar_name=sar_name, clkdist_name=clkdist_name, rdac_name=rdac_name, space_1x_name=space_1x_name,
                 placement_grid=pg, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5, routing_grid_m4m5_basic_thick=rg_m4m5_basic_thick,
                 routing_grid_m5m6=rg_m5m6,
                 routing_grid_m5m6_thick=rg_m5m6_thick, routing_grid_m5m6_basic_thick=rg_m5m6_basic_thick,
                 routing_grid_m5m6_thick_basic=rg_m5m6_thick_basic, 
                 routing_grid_m6m7_thick=rg_m6m7_thick, routing_grid_m7m8_thick=rg_m7m8_thick,
                 num_inv_bb=num_inv_bb, num_bits=num_bits, num_slices=num_slices, clk_pulse=clk_pulse, slice_order=slice_order, trackm=trackm, origin=np.array([0, 0]))
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
