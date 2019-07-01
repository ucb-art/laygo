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
#import logging;logging.basicConfig(level=logging.DEBUG)

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)


def generate_sarclkdelayslice_compact2(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4,
                       m=2, ndelay=1, origin=np.array([0, 0])):
    """generate clock delay """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    #inv_name = 'inv_' + str(m) + 'x'
    #mux_name = 'mux2to1_' + str(m) + 'x'
    inv_name = 'inv_' + str(m) + 'x'
    mux_name = 'mux2to1_1x'

    # placement
    isel0 = laygen.place(name="I" + objectname_pfix + 'INVSEL0', templatename=inv_name,
                         gridname=pg, xy=origin, template_libname=templib_logic)
    refi=isel0.name
    iinvda=[]
    iinvdb=[]
    for i in range(ndelay):
        iinvda.append(laygen.relplace(name="I" + objectname_pfix + 'INVDA'+str(i), templatename=inv_name,
                                      gridname=pg, refinstname=refi, template_libname=templib_logic))
        refi=iinvda[-1].name
        iinvdb.append(laygen.relplace(name="I" + objectname_pfix + 'INVDB'+str(i), templatename=inv_name,
                                      gridname=pg, refinstname=refi, template_libname=templib_logic))
        refi=iinvdb[-1].name
    imux0 = laygen.relplace(name="I" + objectname_pfix + 'MUX0', templatename=mux_name,
                            gridname=pg, refinstname=refi, template_libname=templib_logic)

    # internal pins
    pdict = laygen.get_inst_pin_xy(None, None, rg_m3m4)

    # internal routes
    x0 = laygen.get_inst_xy(name=isel0.name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=imux0.name, gridname=rg_m3m4)[0]\
         +laygen.get_template_size(name=imux0.cellname, gridname=rg_m3m4, libname=templib_logic)[0] - 1
    y0 = pdict[isel0.name]['I'][0][1] + 0

    #route-sel
    [rsel0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[isel0.name]['I'][0],
                                       pdict[imux0.name]['EN1'][0], y0, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[isel0.name]['O'][0],
                                       pdict[imux0.name]['EN0'][0], y0+1, rg_m3m4)
    #route-input
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][2],
                                       laygen.get_inst_pin_xy(iinvda[0].name, 'I', rg_m2m3)[0],
                                       laygen.get_inst_pin_xy(imux0.name, 'I0', rg_m2m3)[0],
                                       laygen.get_inst_pin_xy(imux0.name, 'I0', rg_m2m3)[0][1]+1, rg_m2m3)
    # [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinvda[0].name]['I'][0],
    #                                    pdict[imux0.name]['I0'][0], y0+2, rg_m3m4)
    #route-path1
    for i in range(ndelay):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinvda[i].name]['O'][0],
                                           pdict[iinvdb[i].name]['I'][0], y0+3, rg_m3m4)
    for i in range(ndelay-1):
        [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinvdb[i].name]['O'][0],
                                           pdict[iinvda[i+1].name]['I'][0], y0+6, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinvdb[-1].name]['O'][0],
                                       pdict[imux0.name]['I1'][0], y0+5, rg_m3m4)

    #pins
    laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=pdict[iinvda[0].name]['I'], gridname=rg_m3m4)
    laygen.pin(name='SEL', layer=laygen.layers['pin'][3], xy=pdict[isel0.name]['I'], gridname=rg_m3m4)
    laygen.pin(name='O', layer=laygen.layers['pin'][3], xy=pdict[imux0.name]['O'], gridname=rg_m3m4)

    # power pin
    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=isel0, inst_right=imux0)


def generate_sarclkdelay_compact_dual(laygen, objectname_pfix, templib_logic, workinglib, placement_grid, routing_grid_m3m4,
                                      m_space_4x=0, m_space_2x=0, m_space_1x=0, fastest=False, origin=np.array([0, 0])):
    """generate clock delay """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    tap_name = 'tap'
    tie_name = 'tie_2x'
    dff_name = 'dff_rsth_1x'
    nor_name = 'nor_2x'
    inv_name = 'inv_1x'
    mux_name = 'mux2to1_1x'
    slice_name = 'sarclkdelayslice_compact'
    space_1x_name = 'space_1x'
    space_2x_name = 'space_2x'
    space_4x_name = 'space_4x'

    # placement
    islice0 = laygen.place(name="I" + objectname_pfix + 'SL0', templatename=slice_name,
                              gridname=pg, xy=origin, template_libname=workinglib)
    islice1 = laygen.relplace(name="I" + objectname_pfix + 'SL1', templatename=slice_name,
                              gridname=pg, refinstname=islice0.name, template_libname=workinglib)
    #islice2 = laygen.relplace(name="I" + objectname_pfix + 'SL2', templatename=slice_name,
    #                          gridname=pg, refinstname=islice1.name, template_libname=workinglib)
    imux0 = laygen.relplace(name="I" + objectname_pfix + 'MUX0', templatename=mux_name,
                              gridname=pg, refinstname=islice1.name, template_libname=templib_logic)
    inor0 = laygen.relplace(name="I" + objectname_pfix + 'NR0', templatename=nor_name,
                              gridname=pg, refinstname=imux0.name, template_libname=templib_logic)
    iinv0 = laygen.relplace(name="I" + objectname_pfix + 'INV0', templatename=inv_name,
                              gridname=pg, refinstname=inor0.name, template_libname=templib_logic)
    isp4x = []
    isp2x = []
    isp1x = []
    refi=islice0.name
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

    # internal pins
    pdict = laygen.get_inst_pin_xy(None, None, rg_m3m4)

    # internal routes
    x0 = laygen.get_inst_xy(name=islice0.name, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_inst_xy(name=iinv0.name, gridname=rg_m3m4)[0]\
         + laygen.get_template_size(name=iinv0.cellname, gridname=rg_m3m4, libname=templib_logic)[0] 
    y0 = pdict[islice0.name]['I'][0][1] + 2

    #route-backtoback
    if fastest == False:
        rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice0.name]['O'][0],
                               pdict[islice1.name]['I'][0], y0, rg_m3m4)
    else:
        rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][2],
                                   laygen.get_inst_pin_xy(islice0.name, 'I', rg_m2m3)[0],
                                   laygen.get_inst_pin_xy(islice0.name, 'VSS', rg_m2m3)[0], rg_m2m3)
    rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice1.name]['O'][0],
                               pdict[imux0.name]['I1'][0], y0-1, rg_m3m4)
    rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice1.name]['I'][0],
                               pdict[imux0.name]['I0'][0], y0+4-8, rg_m3m4)

    #nor-inv
    rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inor0.name]['O'][0],
                               pdict[iinv0.name]['I'][0], y0+1, rg_m3m4)
    #internal en
    rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inor0.name]['O'][0],
                               pdict[imux0.name]['EN0'][0], y0+1, rg_m3m4)
    rv0, rh0, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[iinv0.name]['O'][0],
                               pdict[imux0.name]['EN1'][0], y0+3, rg_m3m4)
    #sel/short/en
    rv0, rsel0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice0.name]['SEL'][0],
                                   np.array([x1, y0-6]), rg_m3m4)
    rv0, rsel1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice1.name]['SEL'][0],
                                   np.array([x1, y0-5]), rg_m3m4)
    rsel2 = laygen.route(None, layer=laygen.layers['metal'][4], xy0=np.array([x1-6, y0-4]), xy1=np.array([x1, y0-4]), gridname0=rg_m3m4)
    #rv0, rsel2 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[islice2.name]['SEL'][0],
    #                               np.array([x1, y0-4]), rg_m3m4)
    #rv0, rshort0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inor0.name]['A'][0],
    #                               np.array([x1, y0-1]), rg_m3m4)
    #rv0, ren0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], pdict[inor0.name]['B'][0],
    #                               np.array([x1, y0]), rg_m3m4)
    #pins
    if fastest==False:
        laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=pdict[islice0.name]['I'], gridname=rg_m3m4)
    else:
        laygen.pin(name='I', layer=laygen.layers['pin'][3], xy=pdict[islice1.name]['I'], gridname=rg_m3m4)
    laygen.pin(name='O', layer=laygen.layers['pin'][3], xy=pdict[imux0.name]['O'], gridname=rg_m3m4)
    laygen.boundary_pin_from_rect(rsel0, rg_m3m4, "SEL<0>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rsel1, rg_m3m4, "SEL<1>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rsel2, rg_m3m4, "SEL<2>", laygen.layers['pin'][4], size=6, direction='right')
    laygen.pin(name='SHORTB', layer=laygen.layers['pin'][3], xy=pdict[inor0.name]['A'], gridname=rg_m3m4)
    laygen.pin(name='ENB', layer=laygen.layers['pin'][3], xy=pdict[inor0.name]['B'], gridname=rg_m3m4)
    #laygen.boundary_pin_from_rect(rshort0, rg_m3m4, "SHORT", laygen.layers['pin'][4], size=6, direction='right')
    #laygen.boundary_pin_from_rect(ren0, rg_m3m4, "EN", laygen.layers['pin'][4], size=6, direction='right')

    # power pin
    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=islice0, inst_right=iinv0)

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

    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'_templates.yaml', libname=workinglib)

    mycell_list = []
    ndelay = 2
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        ndelay=sizedict['sarclkgen']['ndelay']
        fastest = sizedict['sarclkgen']['fastest']

    #cell generation (slice_compact)
    cellname='sarclkdelayslice_compact'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkdelayslice_compact2(laygen, objectname_pfix='DSL0', templib_logic=logictemplib, placement_grid=pg,
                               routing_grid_m3m4=rg_m3m4, m=1, ndelay=ndelay, origin=np.array([0, 0]))
    laygen.add_template_from_cell()

    # dual_array generation
    cellname='sarclkdelay_compact_dual'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarclkdelay_compact_dual(laygen, objectname_pfix='CKD0', templib_logic=logictemplib, workinglib=workinglib,
                         placement_grid=pg, routing_grid_m3m4=rg_m3m4, m_space_4x=0, m_space_2x=0, m_space_1x=0, fastest=fastest,
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
