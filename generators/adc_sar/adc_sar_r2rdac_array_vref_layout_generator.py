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

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0], rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0], rvss1_pin_xy[1])), gridname=gridname)


def generate_r2r_dac_bcap_array(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m4m5, routing_grid_m5m6,
                           rg_m3m4_basic_thick, rg_m5m6_thick, m, num_bits, num_hori, num_vert,
                           origin=np.array([0, 0])):
    """generate r2rdac """
    r2r_name = 'r2r_dac_bcap_vref'
    sar_name = 'sar_wsamp'
    ret_name = 'adc_retimer'
    tgate_name = 'tgate_' + str(m) + 'x'
    pg = placement_grid

    rg_m4m5 = routing_grid_m4m5
    rg_m5m6 = routing_grid_m5m6
    # rg_m4m5 = routing_grid_m4m5
    # rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    # rg_m4m5_thick = routing_grid_m4m5_thick
    # rg_m5m6 = routing_grid_m5m6
    # rg_m5m6_thick = routing_grid_m5m6_thick
    # rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    # rg_m6m7_thick = routing_grid_m6m7_thick

    # Calculate reference coordinate
    x1_phy = laygen.get_template_xy(name=r2r_name, gridname=None, libname=workinglib)[0] * num_hori
    pin_origin_x = laygen.grids.get_absgrid_x(rg_m5m6_thick_basic, x1_phy)
    y1_phy = origin[1] + laygen.get_template_xy(name=sar_name, gridname=None, libname=workinglib)[1] \
             + laygen.get_template_xy(name=ret_name, gridname=None, libname=workinglib)[1]
    pin_origin_y = laygen.grids.get_absgrid_y(rg_m5m6, y1_phy)
    pin_origin_y2_thick = origin[1] + \
                          laygen.get_template_pin_xy(sar_name, 'VREF<2>_M6_0', rg_m5m6_thick, libname=workinglib)[0][1] \
                          + laygen.get_template_xy(name=ret_name, gridname=rg_m5m6_thick, libname=workinglib)[1]
    pin_origin_y1_thick = origin[1] + \
                          laygen.get_template_pin_xy(sar_name, 'VREF<1>_M6_0', rg_m5m6_thick, libname=workinglib)[0][1] \
                          + laygen.get_template_xy(name=ret_name, gridname=rg_m5m6_thick, libname=workinglib)[1]
    pin_origin_y0_thick = origin[1] + \
                          laygen.get_template_pin_xy(sar_name, 'VREF<0>_M6_0', rg_m5m6_thick, libname=workinglib)[0][1] \
                          + laygen.get_template_xy(name=ret_name, gridname=rg_m5m6_thick, libname=workinglib)[1]
    # pin_origin_y0_thick = laygen.grids.get_absgrid_y(rg_m5m6_thick, y0_phy)

    # placement
    irdac = []
    for i in range(num_vert):
        if i == 0:
            irdac.append(laygen.relplace(name="I" + objectname_pfix + 'IBCAP' + str(i), templatename=r2r_name,
                                         gridname=pg, refinstname=None, xy=origin, shape=[num_hori, 1],
                                         template_libname=workinglib))
        else:
            irdac.append(laygen.relplace(name="I" + objectname_pfix + 'IBCAP' + str(i), templatename=r2r_name,
                                         gridname=pg, refinstname=irdac[-1].name, shape=[num_hori, 1],
                                         template_libname=workinglib, direction='top'))

    # output routing
    for k in range(4):
        rv2, rh2 = laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                   xy0=laygen.get_inst_pin_xy(irdac[2].name, 'I', rg_m5m6_thick,
                                                              index=np.array([0, 0]))[0] + np.array([2, 0]),
                                   xy1=np.array([pin_origin_x, pin_origin_y2_thick+k]),
                                   gridname0=rg_m5m6_thick)
        rv1, rh1 = laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                   xy0=laygen.get_inst_pin_xy(irdac[1].name, 'I', rg_m5m6_thick,
                                                              index=np.array([0, 0]))[0] + np.array([1, 0]),
                                   xy1=np.array([pin_origin_x, pin_origin_y1_thick+k]),
                                   gridname0=rg_m5m6_thick)
        rv0, rh0 = laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                   xy0=laygen.get_inst_pin_xy(irdac[0].name, 'I', rg_m5m6_thick,
                                                              index=np.array([0, 0]))[0] + np.array([0, 0]),
                                   xy1=np.array([pin_origin_x, pin_origin_y0_thick+k]),
                                   gridname0=rg_m5m6_thick)
        for j in range(num_vert):
            laygen.via(None, xy=laygen.get_inst_pin_xy(irdac[j].name, 'I', rg_m4m5, index=np.array([0, 0]))[
                                    0] + np.array([j, 0]), gridname=rg_m4m5)
        laygen.boundary_pin_from_rect(rh2, rg_m5m6_thick, 'VREF'+str(k)+'<' + str(2) + '>',
                                      laygen.layers['pin'][6], size=4, direction='right', netname='VREF<' + str(2) + '>')
        laygen.boundary_pin_from_rect(rh1, rg_m5m6_thick, 'VREF'+str(k)+'<' + str(1) + '>',
                                      laygen.layers['pin'][6], size=4, direction='right', netname='VREF<' + str(1) + '>')
        laygen.boundary_pin_from_rect(rh0, rg_m5m6_thick, 'VREF'+str(k)+'<' + str(0) + '>',
                                      laygen.layers['pin'][6], size=4, direction='right', netname='VREF<' + str(0) + '>')

    pin_origin_y2_thick = laygen.grids.get_absgrid_y(rg_m5m6_thick, laygen.grids.get_phygrid_y(rg_m5m6,
                                                                                               pin_origin_y + 4 + num_hori * num_vert))
    # m5 supply
    pdict_m5m6_thick = laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    rvdd_m5 = []
    rvss_m5 = []
    for i in range(num_hori):
        for p in pdict_m5m6_thick[irdac[0].name]:
            if p.startswith('VDD'):
                r0 = laygen.route(None, laygen.layers['metal'][5],
                                  xy0=laygen.get_inst_pin_xy(irdac[0].name, p, rg_m5m6_thick, index=np.array([i, 0]))[
                                      0],
                                  xy1=laygen.get_inst_pin_xy(irdac[num_vert - 1].name, p, rg_m5m6_thick,
                                                             index=np.array([i, 0]))[1],
                                  gridname0=rg_m5m6_thick)
                rvdd_m5.append(r0)
        for p in pdict_m5m6_thick[irdac[0].name]:
            if p.startswith('VSS'):
                r0 = laygen.route(None, laygen.layers['metal'][5],
                                  xy0=laygen.get_inst_pin_xy(irdac[0].name, p, rg_m5m6_thick, index=np.array([i, 0]))[
                                      0],
                                  xy1=laygen.get_inst_pin_xy(irdac[num_vert - 1].name, p, rg_m5m6_thick,
                                                             index=np.array([i, 0]))[1],
                                  gridname0=rg_m5m6_thick)
                rvss_m5.append(r0)

    #m6 (extract VDD/VSS grid from tisar and make power pins)
    tisar_name = 'tisaradc_body_core'
    tisar_libname = 'adc_sar_generated'
    rg_m5m6_thick_temp_tisar='route_M5_M6_thick_temp_tisar_VDD'
    # bnd = laygen.get_template(tisar_name, libname=tisar_libname).xy
    laygenhelper.generate_grids_from_template(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_tisar,
                                              template_name=tisar_name, template_libname=tisar_libname,
                                              template_pin_prefix=['VDD'], bnd=None, xy_grid_type='ygrid')
    input_rails_rect = [rvdd_m5]
    rvdd_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_',
                layer=laygen.layers['pin'][6], gridname=rg_m5m6_thick_temp_tisar, netnames=['VDD'], direction='x',
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    rg_m5m6_thick_temp_tisar='route_M5_M6_thick_temp_tisar_VSS'
    laygenhelper.generate_grids_from_template(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_tisar,
                                              template_name=tisar_name, template_libname=tisar_libname,
                                              template_pin_prefix=['VSS'], xy_grid_type='ygrid')
    input_rails_rect = [rvss_m5]
    rvss_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_',
                layer=laygen.layers['pin'][6], gridname=rg_m5m6_thick_temp_tisar, netnames=['VSS'], direction='x',
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)

def generate_r2r_dac_array(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m4m5, routing_grid_m5m6,
                           rg_m3m4_basic_thick, rg_m5m6_thick, m, num_bits, num_hori, num_vert, origin=np.array([0, 0])):
    """generate r2rdac """
    r2r_name='r2r_dac_vref'
    bcap_name='r2r_dac_bcap_array_vref'
    sar_name='sar_wsamp'
    ret_name='adc_retimer'
    tgate_name = 'tgate_'+str(m)+'x'
    pg = placement_grid

    rg_m4m5 = routing_grid_m4m5
    rg_m5m6 = routing_grid_m5m6
    # rg_m4m5 = routing_grid_m4m5
    # rg_m4m5_basic_thick = routing_grid_m4m5_basic_thick
    # rg_m4m5_thick = routing_grid_m4m5_thick
    # rg_m5m6 = routing_grid_m5m6
    # rg_m5m6_thick = routing_grid_m5m6_thick
    # rg_m5m6_thick_basic = routing_grid_m5m6_thick_basic
    # rg_m6m7_thick = routing_grid_m6m7_thick

    #boundaries
    x0=laygen.templates.get_template('capdac', workinglib).xy[1][0] - \
           laygen.templates.get_template('boundary_bottomleft').xy[1][0]*2
    m_bnd_float = x0 / laygen.templates.get_template('boundary_bottom').xy[1][0]
    m_bnd = int(m_bnd_float)
    if not m_bnd_float == m_bnd:
        m_bnd += 1

    #Calculate reference coordinate
    bcap_origin = np.array([laygen.get_template_xy(name=r2r_name, gridname=pg, libname=workinglib)[0]*num_hori, 0])
    x1_phy = laygen.get_template_xy(name=r2r_name, gridname=None, libname=workinglib)[0]*num_hori \
             + laygen.get_template_xy(name=bcap_name, gridname=None, libname=workinglib)[0]
    pin_origin_x = laygen.grids.get_absgrid_x(rg_m5m6, x1_phy)
    pin_origin_x_thick = laygen.grids.get_absgrid_x(rg_m5m6_thick, x1_phy)
    y1_phy = origin[1] + laygen.get_template_xy(name=sar_name, gridname=None, libname=workinglib)[1] \
                   + laygen.get_template_xy(name=ret_name, gridname=None, libname=workinglib)[1]
    pin_origin_y = laygen.grids.get_absgrid_y(rg_m5m6, y1_phy)
    pin_origin_y2_thick = origin[1] + \
                          laygen.get_template_pin_xy(sar_name, 'VREF<2>_M6_0', rg_m5m6_thick, libname=workinglib)[0][1] \
                          + laygen.get_template_xy(name=ret_name, gridname=rg_m5m6_thick, libname=workinglib)[1]
    pin_origin_y1_thick = origin[1] + \
                          laygen.get_template_pin_xy(sar_name, 'VREF<1>_M6_0', rg_m5m6_thick, libname=workinglib)[0][1] \
                          + laygen.get_template_xy(name=ret_name, gridname=rg_m5m6_thick, libname=workinglib)[1]
    pin_origin_y0_thick = origin[1] + \
                          laygen.get_template_pin_xy(sar_name, 'VREF<0>_M6_0', rg_m5m6_thick, libname=workinglib)[0][1] \
                          + laygen.get_template_xy(name=ret_name, gridname=rg_m5m6_thick, libname=workinglib)[1]
    # pin_origin_y0_thick = laygen.grids.get_absgrid_y(rg_m5m6_thick, y0_phy)

    # placement
    irdac = []
    for i in range(num_vert):
        if i == 0:
            irdac.append(laygen.relplace(name="I" + objectname_pfix + 'IRDAC'+str(i), templatename=r2r_name,
                              gridname=pg, refinstname=None, xy=origin, shape=[num_hori, 1], template_libname=workinglib))
        else:
            irdac.append(laygen.relplace(name="I" + objectname_pfix + 'IRDAC'+str(i), templatename=r2r_name,
                              gridname=pg, refinstname=irdac[-1].name, shape=[num_hori, 1], template_libname=workinglib, direction='top'))
    ibcap = laygen.relplace(name="I" + objectname_pfix + 'IBCAP', templatename=bcap_name,
                    gridname=pg, refinstname=None, xy=bcap_origin, template_libname=workinglib)

    # output routing
    print(pin_origin_x)
    for k in range(4):
        rv2, rh2 = laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                   xy0=laygen.get_inst_pin_xy(irdac[2].name, 'out', rg_m5m6_basic_thick,
                                                              index=np.array([0, 0]))[0] - np.array([2, -1]),
                                   xy1=np.array([pin_origin_x, pin_origin_y2_thick+k]),
                                   gridname0=rg_m5m6_basic_thick)
        rv1, rh1 = laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                   xy0=laygen.get_inst_pin_xy(irdac[1].name, 'out', rg_m5m6_basic_thick,
                                                              index=np.array([0, 0]))[0] - np.array([1, -1]),
                                   xy1=np.array([pin_origin_x, pin_origin_y1_thick+k]),
                                   gridname0=rg_m5m6_basic_thick)
        rv0, rh0 = laygen.route_vh(laygen.layers['metal'][5], laygen.layers['metal'][6],
                                   xy0=laygen.get_inst_pin_xy(irdac[0].name, 'out', rg_m5m6_basic_thick,
                                                              index=np.array([0, 0]))[0] - np.array([0, -1]),
                                   xy1=np.array([pin_origin_x, pin_origin_y0_thick+k]),
                                   gridname0=rg_m5m6_basic_thick)
        for j in range(num_vert):
            laygen.via(None, xy=laygen.get_inst_pin_xy(irdac[j].name, 'out', rg_m4m5, index=np.array([0, 0]))[
                                    0] - np.array([j, 0]), gridname=rg_m4m5)
        laygen.boundary_pin_from_rect(rh2, rg_m5m6_thick, 'VREF'+str(k)+'<' + str(2) + '>',
                                      laygen.layers['pin'][6], size=4, direction='right', netname='VREF<' + str(2) + '>')
        laygen.boundary_pin_from_rect(rh1, rg_m5m6_thick, 'VREF'+str(k)+'<' + str(1) + '>',
                                      laygen.layers['pin'][6], size=4, direction='right', netname='VREF<' + str(1) + '>')
        laygen.boundary_pin_from_rect(rh0, rg_m5m6_thick, 'VREF'+str(k)+'<' + str(0) + '>',
                                      laygen.layers['pin'][6], size=4, direction='right', netname='VREF<' + str(0) + '>')

    # input routing
    # tgate_x = laygen.get_template_xy(tgate_name, gridname=rg_m4m5, libname=logictemplib)[0]
    for i in range(num_hori):
        for j in range(num_vert):
            x_ref = laygen.get_inst_pin_xy(irdac[j].name, 'SEL<0>', rg_m4m5, index=np.array([i, 0]))[1][0]
            for k in range(num_bits):
                rh0, rv0 = laygen.route_hv(laygen.layers['metal'][4], laygen.layers['metal'][5],
                                       xy0=laygen.get_inst_pin_xy(irdac[j].name, 'SEL<'+str(k)+'>', rg_m4m5, index=np.array([i, 0]))[0],
                                       xy1=np.array([x_ref + 12 + num_bits * j + k, 0]), gridname0=rg_m4m5)
                laygen.boundary_pin_from_rect(rv0, rg_m4m5, 'SEL<'+str((num_hori*j+i)*num_bits+k)+'>', laygen.layers['pin'][5], size=4, direction='bottom')

    # m5 supply
    pdict_m5m6_thick = laygen.get_inst_pin_xy(None, None, rg_m5m6_thick)
    rvdd_m5=[]
    rvss_m5=[]
    for i in range(num_hori):
        for p in pdict_m5m6_thick[irdac[0].name]:
            if p.startswith('VDD'):
                r0=laygen.route(None, laygen.layers['metal'][5],
                                xy0=laygen.get_inst_pin_xy(irdac[0].name, p, rg_m5m6_thick, index=np.array([i,0]))[0],
                                xy1=laygen.get_inst_pin_xy(irdac[num_vert-1].name, p, rg_m5m6_thick, index=np.array([i,0]))[1],
                                gridname0=rg_m5m6_thick)
                rvdd_m5.append(r0)
        for p in pdict_m5m6_thick[irdac[0].name]:
            if p.startswith('VSS'):
                r0=laygen.route(None, laygen.layers['metal'][5],
                                xy0=laygen.get_inst_pin_xy(irdac[0].name, p, rg_m5m6_thick, index=np.array([i,0]))[0],
                                xy1=laygen.get_inst_pin_xy(irdac[num_vert-1].name, p, rg_m5m6_thick, index=np.array([i,0]))[1],
                                gridname0=rg_m5m6_thick)
                rvss_m5.append(r0)

    # m6 (extract VDD/VSS grid from tisar and make power pins)
    tisar_name = 'tisaradc_body_core'
    tisar_libname = 'adc_sar_generated'
    rg_m5m6_thick_temp_tisar = 'route_M5_M6_thick_temp_tisar_VDD'
    # x_end = laygen.get_template_xy(r2r_name, gridname=rg_m5m6_thick_temp_tisar, libname=workinglib)[0] + \
    #         laygen.get_template_xy(bcap_name, gridname=rg_m5m6_thick_temp_tisar, libname=workinglib)[0]
    bnd = laygen.get_template(tisar_name, libname=tisar_libname).xy
    laygenhelper.generate_grids_from_template(laygen, gridname_input=rg_m5m6_thick,
                                              gridname_output=rg_m5m6_thick_temp_tisar,
                                              template_name=tisar_name, template_libname=tisar_libname,
                                              template_pin_prefix=['VDDSAR'], bnd=bnd, xy_grid_type='ygrid')

    laygen.grids.display(libname=None, gridname=rg_m5m6_thick_temp_tisar)
    input_rails_rect = [rvdd_m5]
    rvdd_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_',
                                                                layer=laygen.layers['pin'][6],
                                                                gridname=rg_m5m6_thick_temp_tisar, netnames=['VDD'],
                                                                direction='x',
                                                                input_rails_rect=input_rails_rect, generate_pin=True,
                                                                overwrite_start_coord=None, overwrite_end_coord=pin_origin_x_thick,
                                                                offset_start_index=0, offset_end_index=0)
    rg_m5m6_thick_temp_tisar = 'route_M5_M6_thick_temp_tisar_VSS'
    laygenhelper.generate_grids_from_template(laygen, gridname_input=rg_m5m6_thick,
                                              gridname_output=rg_m5m6_thick_temp_tisar,
                                              template_name=tisar_name, template_libname=tisar_libname,
                                              template_pin_prefix=['VSS'], xy_grid_type='ygrid')
    laygen.grids.display(libname=None, gridname=rg_m5m6_thick_temp_tisar)
    input_rails_rect = [rvss_m5]
    rvss_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_',
                                                                layer=laygen.layers['pin'][6],
                                                                gridname=rg_m5m6_thick_temp_tisar, netnames=['VSS'],
                                                                direction='x',
                                                                input_rails_rect=input_rails_rect, generate_pin=True,
                                                                overwrite_start_coord=None, overwrite_end_coord=pin_origin_x_thick,
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
    ret_libname = 'adc_retimer_ec'
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
    rg_m3m4_basic_thick = 'route_M3_M4_basic_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m4m5_basic_thick = 'route_M4_M5_basic_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m5m6_thick_basic = 'route_M5_M6_thick_basic'
    rg_m5m6_basic_thick = 'route_M5_M6_basic_thick'
    rg_m5m6_thick2_thick = 'route_M5_M6_thick2_thick'
    rg_m6m7_thick = 'route_M6_M7_thick'
    rg_m6m7_thick2_thick = 'route_M6_M7_thick2_thick'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    mycell_list = []
    num_bits=9
    num_slices=9
    slice_order=[0,2,4,6,1,3,5,7]
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        num_bits=sizedict['r2rdac_vref']['num_bits']
        num_slices=specdict['n_interleave']
        slice_order=sizedict['slice_order']
        m=sizedict['r2rdac_vref']['m']
        num_series=sizedict['r2rdac_vref']['num_series']
        # num_hori=sizedict['r2rdac_array_vref']['num_hori']
        # num_vert=sizedict['r2rdac_array_vref']['num_vert']

    # r2r dac bcap
    cellname = 'r2r_dac_bcap_array_vref'
    print(cellname + " generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_r2r_dac_bcap_array(laygen, objectname_pfix='R2R_BCAP_ARRAY', templib_logic=logictemplib, placement_grid=pg, routing_grid_m4m5=rg_m4m5_thick,
                       routing_grid_m5m6=rg_m5m6, rg_m3m4_basic_thick=rg_m3m4_basic_thick, rg_m5m6_thick=rg_m5m6_thick,
                       m=m, num_bits=num_bits, num_hori=1, num_vert=3, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    # r2r dac
    cellname = 'r2r_dac_array_vref'
    print(cellname + " generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_r2r_dac_array(laygen, objectname_pfix='R2R_ARRAY', templib_logic=logictemplib, placement_grid=pg, routing_grid_m4m5=rg_m4m5,
                       routing_grid_m5m6=rg_m5m6, rg_m3m4_basic_thick=rg_m3m4_basic_thick, rg_m5m6_thick=rg_m5m6_thick,
                       m=m, num_bits=num_bits, num_hori=1, num_vert=3, origin=np.array([0, 0]))
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
