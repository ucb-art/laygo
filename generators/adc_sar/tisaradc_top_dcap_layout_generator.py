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

def generate_cap(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                 cap_1x_name='space_1x', cap_2x_name='dcap_2x', cap_4x_name='dcap_4x',
                 m_cap_4x=0, m_cap_2x=0, m_cap_1x=0, origin=np.array([0, 0])):
    """generate cap row """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tap_name = 'tap'

    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                         gridname = pg, xy=origin, template_libname = templib_logic)
    isp4x = []
    isp2x = []
    isp1x = []
    refi=itapl.name
    if not m_cap_4x==0:
        isp4x.append(laygen.relplace(name="I" + objectname_pfix + 'SP4X0', templatename=cap_4x_name,
                     shape = np.array([m_cap_4x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp4x[-1].name
    if not m_cap_2x==0:
        isp2x.append(laygen.relplace(name="I" + objectname_pfix + 'SP2X0', templatename=cap_2x_name,
                     shape = np.array([m_cap_2x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp2x[-1].name
    if not m_cap_1x==0:
        isp1x.append(laygen.relplace(name="I" + objectname_pfix + 'SP1X0', templatename=cap_1x_name,
                     shape=np.array([m_cap_1x, 1]), gridname=pg,
                     refinstname=refi, template_libname=templib_logic))
        refi = isp1x[-1].name
    itapr=laygen.relplace(name = "I" + objectname_pfix + 'TAPR0', templatename = tap_name,
                          gridname = pg, refinstname = refi, template_libname = templib_logic)
    # bias pin if needed
    if 'I' in laygen.templates.get_template(cap_4x_name, templib_logic).pins:
        ri=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m3m4_thick,
                        refinstname0=isp4x[0].name, refpinname0='I', refinstindex0=np.array([0, 0]),
                        refinstname1=isp4x[0].name, refpinname1='I', refinstindex1=np.array([m_cap_4x-1, 0]))
        for i in range(m_cap_4x):
            laygen.via(None, np.array([0, 0]), refinstname=isp4x[0].name, refpinname='I', refinstindex=np.array([i, 0]),
                       gridname=rg_m3m4_thick)
        laygen.pin_from_rect('I', laygen.layers['pin'][4], ri, gridname=rg_m3m4_thick)

    # power pin
    pwr_dim=laygen.get_template_size(name=itapl.cellname, gridname=rg_m2m3, libname=itapl.libname)
    rvdd = []
    rvss = []
    rp1='VDD'
    rvdd_m4=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([pwr_dim[0], 0]), gridname0=rg_m3m4_thick,
                         refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                         refinstname1=itapr.name, refpinname1='VDD', refinstindex1=np.array([0, 0]))
    rvss_m4=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([0, 0]), xy1=np.array([pwr_dim[0], 0]), gridname0=rg_m3m4_thick,
                         refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                         refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0]))
    laygen.pin_from_rect('VDD', laygen.layers['pin'][4], rvdd_m4, gridname=rg_m3m4_thick)
    laygen.pin_from_rect('VSS', laygen.layers['pin'][4], rvss_m4, gridname=rg_m3m4_thick)
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, 0]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, 0]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.via(None, np.array([2*i, 0]), refinstname=itapl.name, refpinname='VDD', refinstindex=np.array([0, 0]),
                   gridname=rg_m3m4_thick)
        laygen.via(None, np.array([2*i+1, 0]), refinstname=itapl.name, refpinname='VSS', refinstindex=np.array([0, 0]),
                   gridname=rg_m3m4_thick)
        #laygen.pin_from_rect('VDD'+str(2*i-2), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        #laygen.pin_from_rect('VSS'+str(2*i-2), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, 0]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, 0]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.via(None, np.array([2*i+2+1, 0]), refinstname=itapr.name, refpinname='VDD', refinstindex=np.array([0, 0]),
                   gridname=rg_m3m4_thick)
        laygen.via(None, np.array([2*i+2, 0]), refinstname=itapr.name, refpinname='VSS', refinstindex=np.array([0, 0]),
                   gridname=rg_m3m4_thick)
        #laygen.pin_from_rect('VDD'+str(2*i-1), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        #laygen.pin_from_rect('VSS'+str(2*i-1), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
    for j in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), addvia0=True,
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), addvia1=True))
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2+1, 0]), xy1=np.array([2*j+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), addvia0=True,
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2, 0]), xy1=np.array([2*j+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), addvia1=True))

def generate_cap_wbnd(laygen, objectname_pfix, workinglib, cap_name, placement_grid, m=1, shape=np.array([1, 1]), origin=np.array([0, 0])):
    cap_origin = origin + laygen.get_template_size('boundary_bottomleft', pg)
    icap=[]
    for i in range(m):
        if i==0:
            icap.append(laygen.place(name="I" + objectname_pfix + 'SP0', templatename=cap_name,
                              gridname=pg, xy=cap_origin, shape=shape, template_libname=workinglib))
        else:
            if i%2==0:
                icap.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(i), templatename=cap_name,
                            gridname=pg, refinstname=icap[-1].name, shape=shape, template_libname=workinglib, direction='top'))
            else:
                icap.append(laygen.relplace(name="I" + objectname_pfix + 'SP' + str(i), templatename=cap_name,
                            gridname=pg, refinstname=icap[-1].name, shape=shape, template_libname=workinglib, direction='top', transform='MX'))
    xy0=laygen.get_template_size(name=cap_name, gridname=pg, libname=workinglib)*shape
    xsp=xy0[0]
    #ysp=xy0[1]
    m_bnd = int(xsp / laygen.get_template_size('boundary_bottom', gridname=pg)[0])
    devname_left=[]
    devname_right=[]
    transform_left=[]
    transform_right=[]
    for i in range(m):
        if i%2==0:
            devname_left+=['nmos4_fast_left', 'pmos4_fast_left']
            devname_right+=['nmos4_fast_right', 'pmos4_fast_right']
            transform_left+=['R0', 'MX']
            transform_right+=['R0', 'MX']
        else:
            devname_left+=['pmos4_fast_left', 'nmos4_fast_left']
            devname_right+=['pmos4_fast_right', 'nmos4_fast_right']
            transform_left+=['MX', 'R0']
            transform_right+=['MX', 'R0']
    [bnd_bottom, bnd_top, bnd_left, bnd_right] \
        = laygenhelper.generate_boundary(laygen, objectname_pfix='BND0', placement_grid=pg,
                            devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
                            shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
                            shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
                            devname_left=devname_left,
                            transform_left=transform_left,
                            devname_right=devname_right,
                            transform_right=transform_right,
                            origin=origin)
    pdict_m3m4_thick=laygen.get_inst_pin_coord(None, None, rg_m3m4_thick)
    for i in range(int((m+1)/2)):
        pxyvdd=pdict_m3m4_thick[icap[i*2].name]['VDD']
        pxyvdd[1] = pxyvdd[0]+(pxyvdd[1]-pxyvdd[0])*shape
        pxyvss=pdict_m3m4_thick[icap[i*2].name]['VSS']
        pxyvss[1] = pxyvss[0]+(pxyvss[1]-pxyvss[0])*shape
        laygen.pin('VDD'+str(i), laygen.layers['pin'][4], pdict_m3m4_thick[icap[i*2].name]['VDD'], gridname=rg_m3m4_thick, netname='VDD')
        laygen.pin('VSS'+str(i), laygen.layers['pin'][4], pdict_m3m4_thick[icap[i*2].name]['VSS'], gridname=rg_m3m4_thick, netname='VSS')
    cap_template = laygen.templates.get_template(cap_name, workinglib)
    cap_pins=cap_template.pins
    if 'I' in cap_pins:
        if m==1:
            laygen.pin('I', laygen.layers['pin'][4], pdict_m3m4_thick[icap[i].name]['I'], gridname=rg_m3m4_thick)
        else:
            for i in range(int(m)):
                laygen.pin('I<'+str(i)+'>', laygen.layers['pin'][4], pdict_m3m4_thick[icap[i].name]['I'], gridname=rg_m3m4_thick)

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
    rg_m7m8_thick = 'route_M7_M8_thick'

    mycell_list = []

    #biascap generation
    #calculate # of cap cells to be inserted
    x0 = laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('tap', libname=logictemplib).xy[1][0] * 2 \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = 200
    m_cap_4x = 20
    m_space_2x= 0
    m_space_1x= 0
    #generate
    cellname = 'TISARADC_bcap_row'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap(laygen, objectname_pfix='CAP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                 cap_1x_name='space_1x', cap_2x_name='space_2x', cap_4x_name='bcap2_8x',
                 m_cap_4x=m_cap_4x, m_cap_2x=m_space_2x, m_cap_1x=m_space_1x, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    cellname_core=cellname
    cellname = 'TISARADC_bcap'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap_wbnd(laygen, objectname_pfix='CAP0', workinglib=workinglib, cap_name=cellname_core, placement_grid=pg, m=20, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    biascap_name=cellname
    '''
    #dcap generation(lower side)
    #calculate # of cap cells to be inserted
    x0 = laygen.templates.get_template(cellname, libname=workinglib).xy[1][0] \
         - laygen.templates.get_template('tap', libname=logictemplib).xy[1][0] * 2 \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_cap_4x=int(m_space/10) #x10 instead of x4..needs to be fixed
    m_space_2x=int((m_space-m_cap_4x*10)/2)
    m_space_1x=int(m_space-m_cap_4x*10-m_space_2x*2)
    #generate
    cellname = 'sarbias_'+str(num_slices)+'slice_sfarray_dcap_lower_core'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap(laygen, objectname_pfix='CAP0', templib_logic=logictemplib, placement_grid=pg, routing_grid_m3m4=rg_m3m4,
                 cap_1x_name='space_1x', cap_2x_name='space_2x', cap_4x_name='dcap2_8x',
                 m_cap_4x=m_cap_4x, m_cap_2x=m_space_2x, m_cap_1x=m_space_1x, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    cellname_core=cellname
    cellname = 'sarbias_'+str(num_slices)+'slice_sfarray_dcap_lower'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_cap_wbnd(laygen, objectname_pfix='CAP0', workinglib=workinglib, cap_name=cellname_core, placement_grid=pg, m=4, origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    dcap_lower_name=cellname
    '''

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
