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
#from logic_layout_generator import *
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

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)


def generate_space_dcap(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                        m_dcap=0, m_space_4x=0, m_space_2x=0, m_space_1x=0, dcap_name='dcap2_8x', origin=np.array([0, 0])):
    """generate space row """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tap_name = 'tap'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'
    #dcap_name = 'dcap2_8x'

    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                         gridname = pg, xy=origin, template_libname = templib_logic)
    idcap = []
    isp4x = []
    isp2x = []
    isp1x = []
    refi=itapl.name
    if not m_dcap==0:
        idcap.append(laygen.relplace(name="I" + objectname_pfix + 'DCAP0', templatename=dcap_name,
                     shape = np.array([m_dcap, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = idcap[-1].name
    if not m_space_4x==0:
        isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X0', templatename=space_4x_name,
                     shape = np.array([m_space_4x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp4x[-1].name
    if not m_space_2x==0:
        isp2x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2X0', templatename=space_2x_name,
                     shape = np.array([m_space_2x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp2x[-1].name
    if not m_space_1x==0:
        isp1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP1X0', templatename=space_1x_name,
                     shape=np.array([m_space_1x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp1x[-1].name
    itapr=laygen.relplace(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                          gridname = pg, refinstname = refi, template_libname = templib_logic)

    # power pin
    pwr_dim=laygen.get_xy(obj =itapl.template, gridname=rg_m2m3)
    rvdd = []
    rvss = []
    rp1='VDD'
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin(name = 'VDD'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(2*i-2), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, 0]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin(name = 'VDD'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(2*i-1), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')
    for j in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2+1, 0]), xy1=np.array([2*j+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[[0, 0]],
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2, 0]), xy1=np.array([2*j+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[[0, 0]]))

    yamlfile_output="adc_sar_size.yaml"
    #write to file
    with open(yamlfile_output, 'r') as stream:
        outdict = yaml.load(stream)
    outdict['m_dcap2']=m_dcap
    with open(yamlfile_output, 'w') as stream:
        yaml.dump(outdict, stream)

def generate_space_wbnd(laygen, objectname_pfix, workinglib, space_name, placement_grid, origin=np.array([0, 0])):
    space_origin = origin + laygen.get_xy(obj=laygen.get_template(name = 'boundary_bottomleft'), gridname = pg)
    ispace=laygen.place(name="I" + objectname_pfix + 'SP0', templatename=space_name,
                         gridname=pg, xy=space_origin, template_libname=workinglib)
    xy0=laygen.get_xy(obj=laygen.get_template(name=space_name, libname=workinglib), gridname=pg)
    xsp=xy0[0]
    #ysp=xy0[1]
    m_bnd = int(xsp / laygen.get_xy(obj=laygen.get_template(name = 'boundary_bottom'), gridname=pg)[0])
    [bnd_bottom, bnd_top, bnd_left, bnd_right] \
        = laygenhelper.generate_boundary(laygen, objectname_pfix='BND0', placement_grid=pg,
                            devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
                            shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
                            shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_left=['nmos4_fast_left', 'pmos4_fast_left'],
                            transform_left=['R0', 'MX'],
                            devname_right=['nmos4_fast_right', 'pmos4_fast_right'],
                            transform_right=['R0', 'MX'],
                            origin=origin)
    #pins
    space_template = laygen.templates.get_template(space_name, workinglib)
    space_pins=space_template.pins
    space_origin_phy = ispace.bbox[0]
    vddcnt=0
    vsscnt=0
    for pn, p in space_pins.items():
        if pn.startswith('VDD'):
            laygen.add_pin('VDD' + str(vddcnt), 'VDD', space_origin_phy+p['xy'], p['layer'])
            vddcnt += 1
        if pn.startswith('VSS'):
            laygen.add_pin('VSS' + str(vsscnt), 'VSS', space_origin_phy+p['xy'], p['layer'])
            vsscnt += 1


def generate_space_array(laygen, objectname_pfix,
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
    # laygen.add_rect(None, np.array([origin, origin+space_xy+2*tbnd_bleft.size[0]*np.array([1, 0])]), laygen.layers['prbnd'])
    # num_space_tot=int((ttisar.size[1]-2*tbnd_bottom.size[1])/tspace.size[1])
    # tbnd_bleft_size=tbnd_bleft.size

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

    num_unit_row=4
    num_unit_col=3
    ispace_sar = []
    for col in range(num_unit_col):
        ispace_sar.append([])
        space_origin = origin + [col* laygen.get_template_xy(space_name, pg, workinglib)[0],0]
        ispace_sar[col].append(laygen.place(name="I" + objectname_pfix + 'SPSAR' + str(col), templatename=space_name,
                            gridname=pg, xy=space_origin, template_libname=space_libname))

        for i in range(1, num_unit_row):
            if i % 2 == 0:
                ispace_sar[col].append(laygen.relplace(name="I" + objectname_pfix + 'SPSAR' + str(col) + str(i), templatename=space_name,
                                       gridname=pg, refinstname=ispace_sar[col][-1].name, direction='top', transform='R0',
                                       template_libname=space_libname))
            else:
                ispace_sar[col].append(laygen.relplace(name="I" + objectname_pfix + 'SPSAR' + str(col) + str(i), templatename=space_name,
                                       gridname=pg, refinstname=ispace_sar[col][-1].name, direction='top', transform='MX',
                                       template_libname=space_libname))
    #
    # m_bnd = int(space_xy[0] / tbnd_bottom.size[0])
    # [bnd_bottom, bnd_top, bnd_left, bnd_right] \
    #     = laygenhelper.generate_boundary(laygen, objectname_pfix='BNDSAR0', placement_grid=pg,
    #                         devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
    #                         shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
    #                         devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
    #                         shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
    #                         devname_left=devname_bnd_left,
    #                         transform_left=transform_bnd_left,
    #                         devname_right=devname_bnd_right,
    #                         transform_right=transform_bnd_right,
    #                         origin=origin)

    # #vddsamp cap
    # num_space_samp=num_space_tot-num_space_sar-1
    # space_origin = origin + laygen.get_xy(obj=laygen.get_template(name = 'boundary_bottomleft'), gridname = pg) * np.array([1, (3 + 2 * num_space_sar)])
    # ispace_samp = [laygen.place(name="I" + objectname_pfix + 'SPSAMP0', templatename=space_name,
    #                       gridname=pg, xy=space_origin, template_libname=space_libname)]
    # devname_bnd_left = ['nmos4_fast_left', 'pmos4_fast_left']
    # devname_bnd_right = ['nmos4_fast_right', 'pmos4_fast_right']
    # transform_bnd_left = ['R0', 'MX']
    # transform_bnd_right = ['R0', 'MX']
    #
    # for i in range(1, num_space_samp):
    #     if i % 2 == 0:
    #         ispace_samp.append(laygen.relplace(name="I" + objectname_pfix + 'SPSAMP' + str(i), templatename=space_name,
    #                                    gridname=pg, refinstname=ispace_samp[-1].name, direction='top', transform='R0',
    #                                    template_libname=space_libname))
    #         devname_bnd_left += ['nmos4_fast_left', 'pmos4_fast_left']
    #         devname_bnd_right += ['nmos4_fast_right', 'pmos4_fast_right']
    #         transform_bnd_left += ['R0', 'MX']
    #         transform_bnd_right += ['R0', 'MX']
    #     else:
    #         ispace_samp.append(laygen.relplace(name="I" + objectname_pfix + 'SPSAMP' + str(i), templatename=space_name,
    #                                    gridname=pg, refinstname=ispace_samp[-1].name, direction='top', transform='MX',
    #                                    template_libname=space_libname))
    #         devname_bnd_left += ['pmos4_fast_left', 'nmos4_fast_left']
    #         devname_bnd_right += ['pmos4_fast_right', 'nmos4_fast_right']
    #         transform_bnd_left += ['R0', 'MX']
    #         transform_bnd_right += ['R0', 'MX']
    #
    # m_bnd = int(space_xy[0] / tbnd_bottom.size[0])
    # [bnd_bottom, bnd_top, bnd_left, bnd_right] \
    #     = laygenhelper.generate_boundary(laygen, objectname_pfix='BNDSAMP0', placement_grid=pg,
    #                                      devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
    #                                      shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
    #                                      devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
    #                                      shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
    #                                      devname_left=devname_bnd_left,
    #                                      transform_left=transform_bnd_left,
    #                                      devname_right=devname_bnd_right,
    #                                      transform_right=transform_bnd_right,
    #                                      origin=space_origin-laygen.get_xy(obj=laygen.get_template(name = 'boundary_bottomleft'), gridname = pg))
    #vdd/vss
    #m3
    rvdd_sar_xy_m3=[]
    rvss_sar_xy_m3=[]
    space_template = laygen.templates.get_template(space_name, workinglib)
    space_pins=space_template.pins
    vddcnt=0
    vsscnt=0
    for col in range(num_unit_col):
        space_origin_phy = ispace_sar[col][0].bbox[0]
        for pn, p in space_pins.items():
            if pn.startswith('VDD'):
                pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_unit_row])])
                pxy[0][1]=y_vddsar_lower_max
                pxy[1][1]=ispace_sar[0][-1].bbox[1][1]
                laygen.add_rect(None, pxy, laygen.layers['metal'][3])
                rvdd_sar_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
                vddcnt += 1
            if pn.startswith('VSS'):
                pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_unit_row])])
                pxy[0][1]=y_vddsar_lower_max
                pxy[1][1]=ispace_sar[0][-1].bbox[1][1]
                laygen.add_rect(None, pxy, laygen.layers['metal'][3])
                rvss_sar_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
                vsscnt += 1

    print(vddcnt, vsscnt)
    # rvdd_samp_xy_m3=[]
    # rvss_samp_xy_m3=[]
    # space_template = laygen.templates.get_template(space_name, workinglib)
    # space_pins=space_template.pins
    # space_origin_phy = ispace_samp[0].bbox[0]
    # vddcnt=0
    # vsscnt=0
    # for pn, p in space_pins.items():
    #     if pn.startswith('VDD'):
    #         pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_space_samp])])
    #         laygen.add_rect(None, pxy, laygen.layers['metal'][3])
    #         rvdd_samp_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
    #         vddcnt += 1
    #     if pn.startswith('VSS'):
    #         pxy=space_origin_phy+np.array([p['xy'][0], p['xy'][1]*np.array([1, num_space_samp])])
    #         laygen.add_rect(None, pxy, laygen.layers['metal'][3])
    #         rvss_samp_xy_m3.append(laygen.grids.get_absgrid_coord_region(gridname=rg_m3m4_thick, xy0=pxy[0], xy1=pxy[1]))
    #         vsscnt += 1
    #m4
    # input_rails_xy = [rvdd_samp_xy_m3, rvss_samp_xy_m3]
    # rvdd_samp_m4, rvss_samp_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_M4_SAMP_', layer=laygen.layers['metal'][4],
    #                                     gridname=rg_m3m4_thick, netnames=['VDDSAMP', 'VSSSAMP'], direction='x',
    #                                     input_rails_xy=input_rails_xy, generate_pin=False,
    #                                     overwrite_start_coord=None, overwrite_end_coord=None,
    #                                     offset_start_index=0, offset_end_index=0)
    end = laygen.get_xy(obj = ispace_sar[-1][0], gridname=rg_m3m4_thick)[0]\
         +laygen.get_xy(obj = ispace_sar[-1][0].template, gridname=rg_m3m4_thick)[0]
    input_rails_xy = [rvdd_sar_xy_m3, rvss_sar_xy_m3]
    rvdd_sar_m4, rvss_sar_m4 = laygenhelper.generate_power_rails_from_rails_xy(laygen, routename_tag='_M4_', layer=laygen.layers['metal'][4],
                                        gridname=rg_m3m4_thick, netnames=['VDD', 'VSS'], direction='x',
                                        input_rails_xy=input_rails_xy, generate_pin=False,
                                        overwrite_start_coord=0, overwrite_end_coord=end,
                                        offset_start_index=0, offset_end_index=0)

    end = laygen.get_xy(obj = ispace_sar[-1][-1], gridname=rg_m4m5_thick)[1]
    if num_unit_row % 2==1:
        end= end +laygen.get_xy(obj = ispace_sar[-1][0].template, gridname=rg_m4m5_thick)[1]
    input_rails_rect = [rvdd_sar_m4, rvss_sar_m4]
    rvdd_sar_m5, rvss_sar_m5 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M5_',
                layer=laygen.layers['metal'][5], gridname=rg_m4m5_thick, netnames=['VDD', 'VSS'], direction='y',
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=end,
                offset_start_index=0, offset_end_index=0)

    end = laygen.get_xy(obj = ispace_sar[-1][0], gridname=rg_m5m6_thick)[0]\
         +laygen.get_xy(obj = ispace_sar[-1][0].template, gridname=rg_m5m6_thick)[0]
    input_rails_rect = [rvdd_sar_m5, rvss_sar_m5]
    rvdd_sar_m6, rvss_sar_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_',
                layer=laygen.layers['metal'][6], gridname=rg_m5m6_thick, netnames=['VDD', 'VSS'], direction='x',
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=end,
                offset_start_index=0, offset_end_index=0)

    end = laygen.get_xy(obj = ispace_sar[-1][-1], gridname=rg_m6m7_thick)[1]
    if num_unit_row % 2 == 1:
        end = end + laygen.get_xy(obj=ispace_sar[-1][0].template, gridname=rg_m6m7_thick)[1]
    input_rails_rect = [rvdd_sar_m6, rvss_sar_m6]
    rvdd_sar_m7, rvss_sar_m7 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M7_',
                layer=laygen.layers['metal'][7], gridname=rg_m6m7_thick, netnames=['VDD', 'VSS'], direction='y',
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=end,
                offset_start_index=1, offset_end_index=0)

    for _idx, _vdd in enumerate(rvdd_sar_m6):
        xy0 = laygen.get_xy(obj=_vdd, gridname=rg_m5m6_thick)
        laygen.pin(name='VDD_M6' + str(_idx), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick,
               netname='VDD')

    for _idx, _vdd in enumerate(rvss_sar_m6):
        xy0 = laygen.get_xy(obj=_vdd, gridname=rg_m5m6_thick)
        laygen.pin(name='VSS_M6' + str(_idx), layer=laygen.layers['pin'][6], xy=xy0, gridname=rg_m5m6_thick,
                       netname='VSS')
    #
    end = laygen.get_xy(obj = ispace_sar[-1][0], gridname=rg_m7m8_thick)[0]\
         +laygen.get_xy(obj = ispace_sar[-1][0].template, gridname=rg_m7m8_thick)[0]
    input_rails_rect = [rvdd_sar_m7, rvss_sar_m7]
    rvdd_sar_m6, rvss_sar_m6 = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M8_',
                layer=laygen.layers['metal'][8], gridname=rg_m7m8_thick, netnames=['VDD', 'VSS'], direction='x',
                input_rails_rect=input_rails_rect, generate_pin=False, overwrite_start_coord=0, overwrite_end_coord=end,
                offset_start_index=0, offset_end_index=0)

    # #m6 (extract VDD/VSS grid from tisar and make power pins)
    # rg_m5m6_sar_vdd='route_M5_M6_thick_temp_tisar_sar_vdd'
    # laygenhelper.generate_grids_from_xy(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_sar_vdd, xy=vddsar_xy, xy_grid_type='ygrid')
    # input_rails_rect = [rvdd_sar_m5]
    # [rvdd_sar_m6] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_SAR_',
    #                         layer=laygen.layers['pin'][6], gridname=rg_m5m6_sar_vdd, netnames=['VDDSAR'], direction='x',
    #                         input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
    #                         offset_start_index=0, offset_end_index=0)
    #
    # rg_m5m6_sar_vss='route_M5_M6_thick_temp_tisar_sar_vss'
    # laygenhelper.generate_grids_from_xy(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_sar_vss, xy=vsssar_xy, xy_grid_type='ygrid')
    # input_rails_rect = [rvss_sar_m5]
    # [rvss_sar_m6] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_SAR_',
    #                         layer=laygen.layers['pin'][6], gridname=rg_m5m6_sar_vss, netnames=['VSS:'], direction='x',
    #                         input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
    #                         offset_start_index=0, offset_end_index=0)
    #
    # rg_m5m6_samp='route_M5_M6_thick_temp_tisar_samp_vdd'
    # laygenhelper.generate_grids_from_xy(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_samp, xy=vddsamp_xy, xy_grid_type='ygrid')
    # input_rails_rect = [rvdd_samp_m5]
    # [rvdd_samp_m6] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_SAMP_',
    #                         layer=laygen.layers['pin'][6], gridname=rg_m5m6_samp, netnames=['VDDSAMP'], direction='x',
    #                         input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
    #                         offset_start_index=0, offset_end_index=0)
    # rg_m5m6_samp='route_M5_M6_thick_temp_tisar_samp_vss'
    # laygenhelper.generate_grids_from_xy(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_samp, xy=vsssamp_xy, xy_grid_type='ygrid')
    # input_rails_rect = [rvss_samp_m5]
    # [rvss_samp_m6] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_SAMP_',
    #                         layer=laygen.layers['pin'][6], gridname=rg_m5m6_samp, netnames=['VSS:'], direction='x',
    #                         input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
    #                         offset_start_index=0, offset_end_index=0)
    #
    # '''
    # rg_m5m6_clkd='route_M5_M6_thick_temp_tisar_clkd'
    # laygenhelper.generate_grids_from_xy(laygen, gridname_input=rg_m5m6_thick, gridname_output=rg_m5m6_clkd, xy=vddclkd_xy + vssclkd_xy, xy_grid_type='ygrid')
    # input_rails_rect = [rvdd_samp_m5, rvss_samp_m5]
    # [rvdd_clkd_m6, rvss_clkd_m6] = laygenhelper.generate_power_rails_from_rails_rect(laygen, routename_tag='_M6_CLKD_',
    #                         layer=laygen.layers['pin'][6], gridname=rg_m5m6_clkd, netnames=['VDDSAMP', 'VSS:'], direction='x',
    #                         input_rails_rect=input_rails_rect, generate_pin=True, overwrite_start_coord=None, overwrite_end_coord=None,
    #                         offset_start_index=0, offset_end_index=0)
    # '''
    # print(num_space_sar, num_space_samp)
    #
    # yamlfile_output="adc_sar_size.yaml"
    # #write to file
    # with open(yamlfile_output, 'r') as stream:
    #     outdict = yaml.load(stream)
    # outdict['num_space_sar']=num_space_sar
    # outdict['num_space_samp']=num_space_samp
    # with open(yamlfile_output, 'w') as stream:
    #     yaml.dump(outdict, stream)


def generate_space_block(laygen, objectname_pfix,
                            tisar_libname, space_libname,
                            tisar_name, space_name,
                            placement_grid, routing_grid_m3m4_thick, routing_grid_m4m5_thick, routing_grid_m5m6_thick,
                            origin=np.array([0, 0])):
    """generate tisar space """
    pg = placement_grid
    ttisar = laygen.templates.get_template(tisar_name, libname=tisar_libname)
    tspace = laygen.templates.get_template(space_name, libname=space_libname)

    num_unit_row=4
    num_unit_col=3
    ispace_sar = []
    for col in range(num_unit_col):
        ispace_sar.append([])
        space_origin = origin + [col* laygen.get_template_xy(space_name, pg, workinglib)[0],0]
        ispace_sar[col].append(laygen.place(name="I" + objectname_pfix + 'SPSAR' + str(col), templatename=space_name,
                            gridname=pg, xy=space_origin, template_libname=space_libname))

        for i in range(1, num_unit_row):
            ispace_sar[col].append(laygen.relplace(name="I" + objectname_pfix + 'SPSAR' + str(col) + str(i), templatename=space_name,
                                       gridname=pg, refinstname=ispace_sar[col][-1].name, direction='top', transform='R0',
                                       template_libname=space_libname))


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
    rg_m3m4_thick = 'route_M3_M4_basic_thick'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m5m6_thick = 'route_M5_M6_thick'
    rg_m6m7_thick = 'route_M6_M7_thick'
    rg_m7m8_thick = 'route_M7_M8_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    tisar_name = 'tisaradc_body_core'

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

    mycell_list = []

    # cellname='decap_unit'
    # print(cellname+" generating")
    # mycell_list.append(cellname)
    # # 1. generate without spacing
    # laygen.add_cell(cellname)
    # laygen.sel_cell(cellname)
    # decap_unit_size = 2 # each unit has nf4
    # generate_space_dcap(laygen, objectname_pfix='SP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
    #                m_dcap=decap_unit_size, m_space_4x=0, m_space_2x=0, m_space_1x=0, origin=np.array([0, 0]))
    # laygen.add_template_from_cell()
    #
    #
    # #space with boundary
    # cellname_wbnd='decap_unit_wbnd'
    # print(cellname_wbnd+" generating")
    # mycell_list.append(cellname_wbnd)
    # laygen.add_cell(cellname_wbnd)
    # laygen.sel_cell(cellname_wbnd)
    # generate_space_wbnd(laygen, objectname_pfix='SP0', workinglib=workinglib, space_name=cellname, placement_grid=pg, origin=np.array([0, 0]))
    # laygen.add_template_from_cell()



    # cell_name = 'decap_unit_array'
    # #space cell generation
    # print(cell_name+" generating")
    # mycell_list.append(cell_name)
    # laygen.add_cell(cell_name)
    # laygen.sel_cell(cell_name)
    # generate_space_array(laygen, objectname_pfix='SP0', tisar_libname=workinglib, space_libname=workinglib,
    #                         tisar_name=tisar_name, space_name='decap_unit_wbnd', placement_grid=pg,
    #                         routing_grid_m3m4_thick=rg_m3m4_thick,
    #                         routing_grid_m4m5_thick=rg_m4m5_thick,
    #                         routing_grid_m5m6_thick=rg_m5m6_thick,
    #                         origin=np.array([0, 0]))
    # laygen.add_template_from_cell()


    cell_name = 'decap_unit_block'
    #space cell generation
    print(cell_name+" generating")
    mycell_list.append(cell_name)
    laygen.add_cell(cell_name)
    laygen.sel_cell(cell_name)
    generate_space_block(laygen, objectname_pfix='SP0', tisar_libname=workinglib, space_libname=workinglib,
                            tisar_name=tisar_name, space_name='decap_unit_array', placement_grid=pg,
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
