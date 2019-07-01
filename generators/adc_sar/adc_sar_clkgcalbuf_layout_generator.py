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

def generate_clkgcalbuf(laygen, objectname_pfix, templib_logic, placement_grid, 
                        routing_grid_m2m3, routing_grid_m3m4, 
                        m_space_4x=0, m_space_2x=0, m_space_1x=0, 
                        origin=np.array([0, 0])):
    """generate a static sar clock generator """
    pg = placement_grid
    rg_m2m3 = routing_grid_m2m3
    rg_m3m4 = routing_grid_m3m4

    tap_name = 'tap'
    inv_name = 'inv_2x'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'

    #m_bnd = 224
    #[bnd_bottom, bnd_top, bnd_left, bnd_right] \
    #    = laygenhelper.generate_boundary(laygen, objectname_pfix='BND0', placement_grid=pg,
    #                        devname_bottom=['boundary_bottomleft', 'boundary_bottom', 'boundary_bottomright'],
    #                        shape_bottom=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
    #                        devname_top=['boundary_topleft', 'boundary_top', 'boundary_topright'],
    #                        shape_top=[np.array([1, 1]), np.array([m_bnd, 1]), np.array([1, 1])],
    #                        devname_left=['nmos4_fast_left', 'pmos4_fast_left', 'pmos4_fast_left', 'nmos4_fast_left'],
    #                        transform_left=['R0', 'MX','R0', 'MX'],
    #                        devname_right=['nmos4_fast_right', 'pmos4_fast_right', 'pmos4_fast_right', 'nmos4_fast_right'],
    #                        transform_right=['R0', 'MX','R0', 'MX'],
    #                        origin=origin - laygen.get_template_size('boundary_bottomleft', pg))
    #origin = origin + laygen.get_template_size('boundary_bottomleft', pg)
    # placement
    itapl = laygen.place(name = "I" + objectname_pfix + 'TAPL0', templatename = tap_name,
                          gridname = pg, xy=origin, template_libname = templib_logic)
    invarr=[]
    refi=itapl.name
    for i in range(8):
        invsubarr=[]
        for j in range(5):
            iinv0 = laygen.relplace(name="I" + objectname_pfix + 'INV' + str(i) + '_' + str(j), templatename=inv_name,
                                    gridname=pg, refinstname=refi, template_libname=templib_logic)
            refi=iinv0.name
            invsubarr.append(iinv0)
        invarr.append(invsubarr)
    isp4x = []
    isp2x = []
    isp1x = []
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
    # internal pins
    pdict_m2m3 = laygen.get_inst_pin_xy(None, None, rg_m2m3)
    pdict = laygen.get_inst_pin_xy(None, None, rg_m3m4)

    # internal routes
    x0 = laygen.get_inst_xy(name=invarr[0][0].name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=invarr[-1][-1].name, gridname=rg_m3m4)[0]\
         +laygen.get_template_size(name=inv_name, gridname=rg_m3m4, libname=templib_logic)[0] - 1
    y0 = pdict[invarr[0][0].name]['I'][0][1] + 0
    # input routes
    # pins
    for i in range(8):
        for j in range(5):
            laygen.pin(name='clkgcal'+str(i)+'<'+str(j)+'>', layer=laygen.layers['pin'][3], xy=pdict[invarr[i][j].name]['I'], gridname=rg_m3m4)
            laygen.pin(name='CLKCAL'+str(i)+'<'+str(j)+'>', layer=laygen.layers['pin'][3], xy=pdict[invarr[i][j].name]['O'], gridname=rg_m3m4)
    ## power route (horizontal)
    ##create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=itapl, inst_right=itapr)
    #laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
    #             refinstname0=itapl.name, refpinname0='VDD', refinstname1=itapr.name, refpinname1='VDD')
    #laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 0]), xy1=np.array([0, 0]), gridname0=rg_m1m2,
    #             refinstname0=itapl.name, refpinname0='VSS', refinstname1=itapr.name, refpinname1='VSS')

    # power pin
    pwr_dim=laygen.get_template_size(name=itapl.cellname, gridname=rg_m2m3, libname=itapl.libname)
    rvdd = []
    rvss = []
    rp1='VDD'
    for i in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i, -10]), xy1=np.array([2*i, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, -10]), xy1=np.array([2*i+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2+1, -10]), xy1=np.array([2*i+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, -10]), xy1=np.array([2*i+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VSS', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1=rp1, refinstindex1=np.array([0, 0])))
        laygen.pin_from_rect('VDD'+str(2*i+1), laygen.layers['pin'][3], rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin_from_rect('VSS'+str(2*i+1), laygen.layers['pin'][3], rvss[-1], gridname=rg_m2m3, netname='VSS')
    for j in range(0, int(pwr_dim[0]/2)):
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j, 0]), xy1=np.array([2*j, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[0,0],
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+1, 0]), xy1=np.array([2*j+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapl.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapl.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[0,0]))
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2+1, 0]), xy1=np.array([2*j+2+1, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]), via0=[0,0],
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0])))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*j+2, 0]), xy1=np.array([2*j+2, 0]), gridname0=rg_m2m3,
                     refinstname0=itapr.name, refpinname0='VDD', refinstindex0=np.array([0, 0]),
                     refinstname1=itapr.name, refpinname1='VSS', refinstindex1=np.array([0, 0]), via1=[0,0]))

def generate_clkgcalbuf_wbnd(laygen, objectname_pfix, workinglib, clkgcalbuf_name, placement_grid, origin=np.array([0, 0])):
    clkgcalbuf_origin = origin + laygen.get_template_size('boundary_bottomleft', pg)
    iclkgcalbuf=laygen.place(name="I" + objectname_pfix + 'SP0', templatename=clkgcalbuf_name,
                         gridname=pg, xy=clkgcalbuf_origin, template_libname=workinglib)
    xy0=laygen.get_template_size(name=clkgcalbuf_name, gridname=pg, libname=workinglib)
    xsp=xy0[0]
    #ysp=xy0[1]
    m_bnd = int(xsp / laygen.get_template_size('boundary_bottom', gridname=pg)[0])
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
    clkgcalbuf_template = laygen.templates.get_template(clkgcalbuf_name, workinglib)
    clkgcalbuf_pins=clkgcalbuf_template.pins
    clkgcalbuf_origin_phy = laygen.get_inst_bbox(iclkgcalbuf.name)[0]
    vddcnt=0
    vsscnt=0
    for pn, p in clkgcalbuf_pins.items():
        if pn.startswith('VDD'):
            laygen.add_pin('VDD' + str(vddcnt), 'VDD', clkgcalbuf_origin_phy+p['xy'], p['layer'])
            vddcnt += 1
        if pn.startswith('VSS'):
            laygen.add_pin('VSS' + str(vsscnt), 'VSS', clkgcalbuf_origin_phy+p['xy'], p['layer'])
            vsscnt += 1
        else:
            laygen.add_pin(pn, p['netname'], clkgcalbuf_origin_phy+p['xy'], p['layer'])

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
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'
    rg_m3m4_thick = 'route_M3_M4_thick'
    rg_m4m5_thick = 'route_M4_M5_thick'
    rg_m5m6_thick = 'route_M5_M6_thick'

    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'_templates.yaml', libname=workinglib)

    mycell_list = []
    #generation 
    cellname='clkgcal'
    print(cellname+" generating")
    mycell_list.append(cellname)
    #1. generate without spacing
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_clkgcalbuf(laygen, objectname_pfix='CKGCAL0', templib_logic=logictemplib, placement_grid=pg,
                        routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4, 
                        m_space_4x=0, m_space_2x=0, m_space_1x=0, 
                        origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    #2. calculate spacing param and regenerate
    num_bits=9
    x0 = laygen.templates.get_template('sarafe_nsw', libname=workinglib).xy[1][0] \
         - laygen.templates.get_template(cellname, libname=workinglib).xy[1][0]  \
         - laygen.templates.get_template('nmos4_fast_left').xy[1][0] * 2
    m_space = int(round(x0 / laygen.templates.get_template('space_1x', libname=logictemplib).xy[1][0]))
    m_space_4x=int(m_space/4)
    m_space_2x=int((m_space-m_space_4x*4)/2)
    m_space_1x=int(m_space-m_space_4x*4-m_space_2x*2)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_clkgcalbuf(laygen, objectname_pfix='CKGCAL0', templib_logic=logictemplib, placement_grid=pg,
                        routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4, 
                        m_space_4x=m_space_4x, m_space_2x=m_space_2x, m_space_1x=m_space_1x, 
                        origin=np.array([0, 0]))
    laygen.add_template_from_cell()
    
    #space with boundary
    cellname_wbnd='clkgcalbuf_wbnd'
    print(cellname_wbnd+" generating")
    mycell_list.append(cellname_wbnd)
    laygen.add_cell(cellname_wbnd)
    laygen.sel_cell(cellname_wbnd)
    generate_clkgcalbuf_wbnd(laygen, objectname_pfix='SP0', workinglib=workinglib, clkgcalbuf_name=cellname, placement_grid=pg, origin=np.array([0, 0]))
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
