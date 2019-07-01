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

def generate_tisaradc_space(laygen, objectname_pfix, tisar_libname, space_libname, tisar_name, space_name,
                            placement_grid, routing_grid_m3m4_thick, routing_grid_m4m5_thick, routing_grid_m5m6_thick, 
                            origin=np.array([0, 0])):
    """generate tisar space """
    pg = placement_grid
    ttisar = laygen.templates.get_template(tisar_name, libname=tisar_libname)
    tspace = laygen.templates.get_template(space_name, libname=space_libname)
    tbnd_bottom = laygen.templates.get_template('boundary_bottom')
    tbnd_bleft = laygen.templates.get_template('boundary_bottomleft')
    space_xy=np.array([tspace.size[0], ttisar.size[1]])
    laygen.add_rect(None, np.array([origin, origin+space_xy+2*tbnd_bleft.size[0]*np.array([1, 0])]), laygen.layers['prbnd'])
    num_space=int((ttisar.size[1]-2*tbnd_bottom.size[1])/tspace.size[1])
    #space_xy=np.array([tspace.size[0], 56.88]) #change it after finishing the clock part
    #num_space=int((56.88-2*tbnd_bottom.size[1])/tspace.size[1]) #should be changed after finishing the clock part
    space_origin = origin + laygen.get_template_size('boundary_bottomleft', pg)
    ispace = [laygen.place(name="I" + objectname_pfix + 'SP0', templatename=space_name,
                          gridname=pg, xy=space_origin, template_libname=space_libname)]
    #devname_bnd_left = ['nmos4_fast_left', 'pmos4_fast_left']
    #devname_bnd_right = ['nmos4_fast_right', 'pmos4_fast_right']
    devname_bnd_left = ['ptap_fast_left', 'ntap_fast_left']
    devname_bnd_right = ['ptap_fast_right', 'ntap_fast_right']
    transform_bnd_left = ['R0', 'MX']
    transform_bnd_right = ['R0', 'MX']
    for i in range(1, num_space):
        if i % 2 == 0:
            ispace.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(i), templatename=space_name,
                                       gridname=pg, refinstname=ispace[-1].name, direction='top', transform='R0',
                                       template_libname=space_libname))
            #devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            #devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            devname_bnd_left += ['ptap_fast_left', 'ntap_fast_left']
            devname_bnd_right += ['ptap_fast_right', 'ntap_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            ispace.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(i), templatename=space_name,
                                       gridname=pg, refinstname=ispace[-1].name, direction='top', transform='MX',
                                       template_libname=space_libname))
            #devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            #devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            devname_bnd_left += ['ntap_fast_left', 'ptap_fast_left']
            devname_bnd_right += ['ntap_fast_right', 'ptap_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
            #transform_bnd_left +=  ['MX', 'R0']
            #transform_bnd_right += ['MX', 'R0']
        
    m_bnd = int(space_xy[0] / tbnd_bottom.size[0])
    [bnd_bottom, bnd_top, bnd_left, bnd_right] \
        = laygenhelper.generate_boundary(laygen, objectname_pfix='BND0', placement_grid=pg,
                            devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
                            shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
                            shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_left=devname_bnd_left,
                            transform_left=transform_bnd_left,
                            devname_right=devname_bnd_right,
                            transform_right=transform_bnd_right,
                            origin=origin)
    #vdd/vss
    #m3
    rvdd_xy_m3=[]
    rvss_xy_m3=[]
    space_template = laygen.templates.get_template(space_name, workinglib)
    space_pins=space_template.pins
    space_origin_phy = laygen.get_inst_bbox_phygrid(ispace[0].name)[0]
    vddcnt=0
    vsscnt=0
    for pn, p in space_pins.items():
        if pn.startswith('VDD'):
            pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_space])])
            laygen.add_rect(None, pxy, p['layer'])
            rvdd_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
            vddcnt += 1
        if pn.startswith('VSS'):
            pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_space])])
            laygen.add_rect(None, pxy, p['layer'])
            rvss_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
            vsscnt += 1
    #m4
    input_rails_xy = [rvdd_xy_m3, rvss_xy_m3]
    rvdd_m4, rvss_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_M4_', layer=laygen.layers['metal'][4], 
                                        gridname=rg_m3m4_thick, netnames=['VDD', 'VSS'], direction='x', 
                                        input_rails_xy=input_rails_xy, generate_pin=False, 
                                        overwrite_start_coord=None, overwrite_end_coord=None, 
                                        overwrite_num_routes=80, offset_start_index=0, offset_end_index=0) 
                                        #exclude_phycoord_list=[[23.4,34.7]])
    #m5
    input_rails_rect = [rvdd_m4, rvss_m4]
    rvdd_m5, rvss_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M5_', 
                layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    #m6 (extract VDD/VSS grid from tisar and make power pins)
    rg_m5m6_thick_temp_tisar='route_M5_M6_thick_temp_tisar_VDD'
    laygenhelper.generate_grids_from_template(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_tisar, 
                                              template_name=tisar_name, template_libname=tisar_libname,
                                              template_pin_prefix=['VDD'], xy_grid_type='ygrid')
    input_rails_rect = [rvdd_m5]
    rvdd_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_', 
                layer=laygen.layers['pin'][6], gridname=rg_m5m6_thick_temp_tisar, netnames=['VDD'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=-1)
    rg_m5m6_thick_temp_tisar='route_M5_M6_thick_temp_tisar_VSS'
    laygenhelper.generate_grids_from_template(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_thick_temp_tisar, 
                                              template_name=tisar_name, template_libname=tisar_libname,
                                              template_pin_prefix=['VSS'], xy_grid_type='ygrid')
    input_rails_rect = [rvss_m5]
    rvss_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_', 
                layer=laygen.layers['pin'][6], gridname=rg_m5m6_thick_temp_tisar, netnames=['VSS'], direction='x', 
                input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=-2)

def generate_tisaradc_space2(laygen, objectname_pfix, 
                            tisar_libname, space_libname,
                            tisar_name, space_name, 
                            placement_grid, routing_grid_m3m4_thick, routing_grid_m4m5_thick, routing_grid_m5m6_thick, 
                            origin=np.array([0, 0])):
    """generate tisar space """
    pg = placement_grid
    ttisar = laygen.templates.get_template(tisar_name, libname=tisar_libname)
    tspace = laygen.templates.get_template(space_name, libname=space_libname)

    sar_pins=ttisar.pins

    tbnd_bottom = laygen.templates.get_template('boundary_bottom')
    tbnd_bleft = laygen.templates.get_template('boundary_bottomleft')
    space_xy=np.array([tspace.size[0], ttisar.size[1]])
    laygen.add_rect(None, np.array([origin, origin+space_xy+2*tbnd_bleft.size[0]*np.array([1, 0])]), laygen.layers['prbnd'])
    num_space_tot=int((ttisar.size[1]-2*tbnd_bottom.size[1])/tspace.size[1])
    tbnd_bleft_size=tbnd_bleft.size

    #VDD/VSS/VREF integration 
    rvddclkd=[]
    rvddsamp=[]
    rvddsar=[]
    rvddsar_upper=[]
    rvref0=[]
    rvref1=[]
    rvref2=[]
    rvssclkd=[]
    rvsssamp=[]
    rvsssar=[]
    rvsssar_upper=[]
    vddclkd_xy=[]
    vddsamp_xy=[]
    vddsar_xy=[]
    vddsar_upper_xy=[]
    vssclkd_xy=[]
    vsssamp_xy=[]
    vsssar_xy=[]
    vsssar_upper_xy=[]
    y_vddsar_max=0
    y_vddsar_lower_max=0
    y_vddsamp_min=500000
    y_vddsamp_max=0
    y_vddclkd_min=500000
    y_vref0=sar_pins['VREF0<0>']['xy'][0][1]

    #categorize vdd pins and figure out thresholds
    for pn, p in sar_pins.items():
        '''
        if pn.startswith('VDDCLKD'):
            pxy=np.array([[0, sar_pins[pn]['xy'][0][1]], 
                          [2*tbnd_bleft_size[0]+space_xy[0], sar_pins[pn]['xy'][1][1]]])
            rvddclkd.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            if pxy[1][1]<y_vddclkd_min:
                y_vddclkd_min=pxy[1][1]
            vddclkd_xy.append(pxy)
        '''
        if pn.startswith('VDDSAMP'):
            pxy=np.array([[0, sar_pins[pn]['xy'][0][1]], 
                          [2*tbnd_bleft_size[0]+space_xy[0], sar_pins[pn]['xy'][1][1]]])
            rvddsamp.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            if pxy[1][1]<y_vddsamp_min:
                y_vddsamp_min=pxy[1][1]
            if pxy[1][1]>y_vddsamp_max:
                y_vddsamp_max=pxy[1][1]
            vddsamp_xy.append(pxy)
        if pn.startswith('VDDSAR'):
            pxy=np.array([[0, sar_pins[pn]['xy'][0][1]], 
                          [2*tbnd_bleft_size[0]+space_xy[0], sar_pins[pn]['xy'][1][1]]])
            if pxy[0][1] > y_vref0:
                rvddsar_upper.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
                vddsar_upper_xy.append(pxy)
            else:
                rvddsar.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
                vddsar_xy.append(pxy)
                if pxy[1][1]>y_vddsar_lower_max:
                    y_vddsar_lower_max=pxy[1][1]
            if pxy[1][1]>y_vddsar_max:
                y_vddsar_max=pxy[1][1]
        if pn.startswith('VREF'):
            pxy=np.array([[0, sar_pins[pn]['xy'][0][1]], 
                          [2*tbnd_bleft_size[0]+space_xy[0], sar_pins[pn]['xy'][1][1]]])
            if pn.endswith('<0>'):
                rvref0.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            if pn.endswith('<1>'):
                rvref1.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
            if pn.endswith('<2>'):
                rvref2.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
    y_vss_th=0.5*(y_vddsar_max+y_vddsamp_min) #find out threshold (sar/samp)
    #y_vss_th2=0.5*(y_vddsamp_max+y_vddclkd_min) #(samp/clkd)
    y_vss_th2=100000
    for pn, p in sar_pins.items():
        if pn.startswith('VSS'):
            pxy=np.array([[0, sar_pins[pn]['xy'][0][1]], 
                          [2*tbnd_bleft_size[0]+space_xy[0], sar_pins[pn]['xy'][1][1]]])
            if pxy[0][1] > y_vss_th2:
                rvssclkd.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
                vssclkd_xy.append(pxy)
            elif pxy[0][1] > y_vss_th:
                rvsssamp.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
                vsssamp_xy.append(pxy)
            elif pxy[0][1] > y_vref0:
                rvsssar_upper.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
                vsssar_upper_xy.append(pxy)
            else:
                rvsssar.append(laygen.add_rect(None, pxy, laygen.layers['metal'][6]))
                vsssar_xy.append(pxy)

    #vddsar cap
    num_space_sar=int((y_vss_th-2*tbnd_bottom.size[1])/tspace.size[1])+4
    space_origin = origin + laygen.get_template_size('boundary_bottomleft', pg)
    ispace_sar = [laygen.place(name="I" + objectname_pfix + 'SPSAR0', templatename=space_name,
                          gridname=pg, xy=space_origin, template_libname=space_libname)]
    devname_bnd_left = ['nmos4_fast_left', 'pmos4_fast_left']
    devname_bnd_right = ['nmos4_fast_right', 'pmos4_fast_right']
    transform_bnd_left = ['R0', 'MX']
    transform_bnd_right = ['R0', 'MX']

    for i in range(1, num_space_sar):
        if i % 2 == 0:
            ispace_sar.append(laygen.relplace(name="I" + objectname_pfix + 'SPSAR' + str(i), templatename=space_name,
                                       gridname=pg, refinstname=ispace_sar[-1].name, direction='top', transform='R0',
                                       template_libname=space_libname))
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            ispace_sar.append(laygen.relplace(name="I" + objectname_pfix + 'SPSAR' + str(i), templatename=space_name,
                                       gridname=pg, refinstname=ispace_sar[-1].name, direction='top', transform='MX',
                                       template_libname=space_libname))
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        
    m_bnd = int(space_xy[0] / tbnd_bottom.size[0])
    [bnd_bottom, bnd_top, bnd_left, bnd_right] \
        = laygenhelper.generate_boundary(laygen, objectname_pfix='BNDSAR0', placement_grid=pg,
                            devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
                            shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
                            shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_left=devname_bnd_left,
                            transform_left=transform_bnd_left,
                            devname_right=devname_bnd_right,
                            transform_right=transform_bnd_right,
                            origin=origin)

    #vddsamp cap
    num_space_samp=num_space_tot-num_space_sar-1
    space_origin = origin + laygen.get_template_size('boundary_bottomleft', pg)*np.array([1, (3+2*num_space_sar)])
    ispace_samp = [laygen.place(name="I" + objectname_pfix + 'SPSAMP0', templatename=space_name,
                          gridname=pg, xy=space_origin, template_libname=space_libname)]
    devname_bnd_left = ['nmos4_fast_left', 'pmos4_fast_left']
    devname_bnd_right = ['nmos4_fast_right', 'pmos4_fast_right']
    transform_bnd_left = ['R0', 'MX']
    transform_bnd_right = ['R0', 'MX']

    for i in range(1, num_space_samp):
        if i % 2 == 0:
            ispace_samp.append(laygen.relplace(name="I" + objectname_pfix + 'SPSAMP' + str(i), templatename=space_name,
                                       gridname=pg, refinstname=ispace_samp[-1].name, direction='top', transform='R0',
                                       template_libname=space_libname))
            devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
            devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']
        else:
            ispace_samp.append(laygen.relplace(name="I" + objectname_pfix + 'SPSAMP' + str(i), templatename=space_name,
                                       gridname=pg, refinstname=ispace_samp[-1].name, direction='top', transform='MX',
                                       template_libname=space_libname))
            devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
            devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
            transform_bnd_left += ['R0', 'MX']
            transform_bnd_right += ['R0', 'MX']

    m_bnd = int(space_xy[0] / tbnd_bottom.size[0])
    [bnd_bottom, bnd_top, bnd_left, bnd_right] \
        = laygenhelper.generate_boundary(laygen, objectname_pfix='BNDSAMP0', placement_grid=pg,
                            devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
                            shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
                            shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_left=devname_bnd_left,
                            transform_left=transform_bnd_left,
                            devname_right=devname_bnd_right,
                            transform_right=transform_bnd_right,
                            origin=space_origin-laygen.get_template_size('boundary_bottomleft', pg))
    #vdd/vss
    #m3
    rvdd_sar_xy_m3=[]
    rvss_sar_xy_m3=[]
    space_template = laygen.templates.get_template(space_name, workinglib)
    space_pins=space_template.pins
    space_origin_phy = laygen.get_inst_bbox_phygrid(ispace_sar[0].name)[0]
    vddcnt=0
    vsscnt=0
    for pn, p in space_pins.items():
        if pn.startswith('VDD'):
            pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_space_sar])])
            pxy[1][1]=y_vddsar_lower_max
            laygen.add_rect(None, pxy, laygen.layers['metal'][3])
            rvdd_sar_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
            vddcnt += 1
        if pn.startswith('VSS'):
            pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_space_sar])])
            pxy[1][1]=y_vddsar_lower_max
            laygen.add_rect(None, pxy, laygen.layers['metal'][3])
            rvss_sar_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
            vsscnt += 1
    rvdd_samp_xy_m3=[]
    rvss_samp_xy_m3=[]
    space_template = laygen.templates.get_template(space_name, workinglib)
    space_pins=space_template.pins
    space_origin_phy = laygen.get_inst_bbox_phygrid(ispace_samp[0].name)[0]
    vddcnt=0
    vsscnt=0
    for pn, p in space_pins.items():
        if pn.startswith('VDD'):
            pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_space_samp])])
            laygen.add_rect(None, pxy, laygen.layers['metal'][3])
            rvdd_samp_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
            vddcnt += 1
        if pn.startswith('VSS'):
            pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_space_samp])])
            laygen.add_rect(None, pxy, laygen.layers['metal'][3])
            rvss_samp_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
            vsscnt += 1
    #m4
    input_rails_xy = [rvdd_samp_xy_m3, rvss_samp_xy_m3]
    rvdd_samp_m4, rvss_samp_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_M4_SAMP_', layer=laygen.layers['metal'][4], 
                                        gridname=rg_m3m4_thick, netnames=['VDDSAMP', 'VSSSAMP'], direction='x', 
                                        input_rails_xy=input_rails_xy, generate_pin=False, 
                                        overwrite_start_coord=None, overwrite_end_coord=None, 
                                        offset_start_index=0, offset_end_index=0) 
    input_rails_xy = [rvdd_sar_xy_m3, rvss_sar_xy_m3]
    rvdd_sar_m4, rvss_sar_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_M4_SAR_', layer=laygen.layers['metal'][4], 
                                        gridname=rg_m3m4_thick, netnames=['VDDSAR', 'VSSSAR'], direction='x', 
                                        input_rails_xy=input_rails_xy, generate_pin=False, 
                                        overwrite_start_coord=None, overwrite_end_coord=None, 
                                        offset_start_index=0, offset_end_index=0) 
    #m5
    input_rails_rect = [rvdd_samp_m4, rvss_samp_m4]
    rvdd_samp_m5, rvss_samp_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M5_SAMP', 
                layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)
    input_rails_rect = [rvdd_sar_m4, rvss_sar_m4]
    rvdd_sar_m5, rvss_sar_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M5_SAR', 
                layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y', 
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=None, overwrite_end_coord=None,
                offset_start_index=0, offset_end_index=0)

    #m6 (extract VDD/VSS grid from tisar and make power pins)
    rg_m5m6_sar_vdd='route_M5_M6_thick_temp_tisar_sar_vdd'
    laygenhelper.generate_grids_from_xy(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_sar_vdd, xy=vddsar_xy, xy_grid_type='ygrid')
    input_rails_rect = [rvdd_sar_m5]
    [rvdd_sar_m6] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_SAR_', 
                            layer=laygen.layers['pin'][6], gridname=rg_m5m6_sar_vdd, netnames=['VDDSAR'], direction='x', 
                            input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                            offset_start_index=0, offset_end_index=0)
    
    rg_m5m6_sar_vss='route_M5_M6_thick_temp_tisar_sar_vss'
    laygenhelper.generate_grids_from_xy(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_sar_vss, xy=vsssar_xy, xy_grid_type='ygrid')
    input_rails_rect = [rvss_sar_m5]
    [rvss_sar_m6] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_SAR_', 
                            layer=laygen.layers['pin'][6], gridname=rg_m5m6_sar_vss, netnames=['VSS:'], direction='x', 
                            input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                            offset_start_index=0, offset_end_index=0)

    rg_m5m6_samp='route_M5_M6_thick_temp_tisar_samp_vdd'
    laygenhelper.generate_grids_from_xy(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_samp, xy=vddsamp_xy, xy_grid_type='ygrid')
    input_rails_rect = [rvdd_samp_m5]
    [rvdd_samp_m6] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_SAMP_', 
                            layer=laygen.layers['pin'][6], gridname=rg_m5m6_samp, netnames=['VDDSAMP'], direction='x', 
                            input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                            offset_start_index=0, offset_end_index=0)
    rg_m5m6_samp='route_M5_M6_thick_temp_tisar_samp_vss'
    laygenhelper.generate_grids_from_xy(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_samp, xy=vsssamp_xy, xy_grid_type='ygrid')
    input_rails_rect = [rvss_samp_m5]
    [rvss_samp_m6] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_SAMP_', 
                            layer=laygen.layers['pin'][6], gridname=rg_m5m6_samp, netnames=['VSS:'], direction='x', 
                            input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                            offset_start_index=0, offset_end_index=0)

    '''
    rg_m5m6_clkd='route_M5_M6_thick_temp_tisar_clkd'
    laygenhelper.generate_grids_from_xy(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_clkd, xy=vddclkd_xy + vssclkd_xy, xy_grid_type='ygrid')
    input_rails_rect = [rvdd_samp_m5, rvss_samp_m5]
    [rvdd_clkd_m6, rvss_clkd_m6] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_CLKD_', 
                            layer=laygen.layers['pin'][6], gridname=rg_m5m6_clkd, netnames=['VDDSAMP', 'VSS:'], direction='x', 
                            input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
                            offset_start_index=0, offset_end_index=0)
    '''
    print(num_space_sar, num_space_samp)

    yamlfile_output="adc_sar_size.yaml"
    #write to file
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    outdict['num_space_sar']=num_space_sar
    outdict['num_space_samp']=num_space_samp
    with open(yamlfile_output, 'w') as stream:
        yaml.dump(outdict, stream)

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
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m3m4_thick = 'route_M3_M4_basic_thick'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m5m6_thick_basic = 'route_M5_M6_thick_basic'
    rg_m5m6_thick2_thick = 'route_M5_M6_thick2_thick'
    rg_m6m7_thick = 'route_M6_M7_thick'
    rg_m6m7_thick2_thick = 'route_M6_M7_thick2_thick'
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

    cellname = 'tisaradc_body_space'
    tisar_name = 'tisaradc_body_core'
    sar_name = 'sar_wsamp'
    #sh_name = 'adc_frontend_sampler_array'
    
    #space_name = 'space'
    space_name = 'space_tap'
    #space cell generation
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_tisaradc_space(laygen, objectname_pfix='TISASP0', tisar_libname=workinglib, space_libname=workinglib, 
                            tisar_name=tisar_name, space_name=space_name, placement_grid=pg, 
                            routing_grid_m3m4_thick=rg_m3m4_thick, 
                            routing_grid_m4m5_thick=rg_m4m5_thick, 
                            routing_grid_m5m6_thick=rg_m5m6_thick, 
                            origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    space_name = 'space_dcap'
    #space cell generation
    cellname = 'tisaradc_body_space2'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_tisaradc_space2(laygen, objectname_pfix='TISASP0', tisar_libname=workinglib, space_libname=workinglib, 
                            tisar_name=tisar_name, space_name=space_name, placement_grid=pg, 
                            routing_grid_m3m4_thick=rg_m3m4_thick, 
                            routing_grid_m4m5_thick=rg_m4m5_thick, 
                            routing_grid_m5m6_thick=rg_m5m6_thick, 
                            origin=np.array([0, 0]))
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
