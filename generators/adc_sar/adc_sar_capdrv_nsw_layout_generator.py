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
#import logging;logging.basicConfig(level=logging.DEBUG)

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)

def generate_capdrv_nsw(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4, m=2, m_space=18, origin=np.array([0, 0])):
    """generate cap driver """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    #inv_name='inv_'+str(m)+'x'
    tg_name='nsw_wovdd_'+str(m)+'x'
    tie_name='tie_wovdd_2x'
    space_1x_name = 'space_wovdd_1x'
    space_2x_name = 'space_wovdd_2x'
    space_4x_name = 'space_wovdd_4x'
    
    #calculate space param
    m_space_4x = int(m_space / 4)
    m_space_2x = int((m_space - m_space_4x * 4) / 2)
    m_space_1x = int(m_space - m_space_4x * 4 - m_space_2x * 2)

    # placement
    it0 = laygen.place(name="I" + objectname_pfix + 'TIE0', templatename=tie_name,
                          gridname=pg, xy=origin, template_libname=templib_logic)
    i3 = laygen.relplace(name = "I" + objectname_pfix + 'TG0', templatename = tg_name,
                         gridname = pg, refinstname = it0.name, template_libname=templib_logic)
    i4 = laygen.relplace(name = "I" + objectname_pfix + 'TG1', templatename = tg_name,
                         gridname = pg, refinstname = i3.name, template_libname=templib_logic)
    i5 = laygen.relplace(name = "I" + objectname_pfix + 'TG2', templatename = tg_name,
                         gridname = pg, refinstname = i4.name, template_libname=templib_logic)
    refi=i5
    if not m_space_4x==0:
        isp4x=laygen.relplace(name="I" + objectname_pfix + 'SP4X0', templatename=space_4x_name,
                     shape = np.array([m_space_4x, 1]), gridname=pg,
                     refinstname=refi.name, template_libname=templib_logic)
        refi = isp4x
    if not m_space_2x==0:
        isp2x=laygen.relplace(name="I" + objectname_pfix + 'SP2X0', templatename=space_2x_name,
                     shape = np.array([m_space_2x, 1]), gridname=pg,
                     refinstname=refi.name, template_libname=templib_logic)
        refi = isp2x
    if not m_space_1x==0:
        isp1x=laygen.relplace(name="I" + objectname_pfix + 'SP1X0', templatename=space_1x_name,
                     shape=np.array([m_space_1x, 1]), gridname=pg,
                     refinstname=refi.name, template_libname=templib_logic)
        refi = isp1x

    # internal pins
    it0_vdd_xy = laygen.get_inst_pin_xy(it0.name, 'TIEVSS2', rg_m3m4)
    it0_vss_xy = laygen.get_inst_pin_xy(it0.name, 'TIEVSS', rg_m3m4)
    i3_en_xy = laygen.get_inst_pin_xy(i3.name, 'EN', rg_m3m4)
    i3_i_xy = laygen.get_inst_pin_xy(i3.name, 'I', rg_m3m4)
    i3_o_xy = laygen.get_inst_pin_xy(i3.name, 'O', rg_m3m4)
    i4_en_xy = laygen.get_inst_pin_xy(i4.name, 'EN', rg_m3m4)
    i4_i_xy = laygen.get_inst_pin_xy(i4.name, 'I', rg_m3m4)
    i4_o_xy = laygen.get_inst_pin_xy(i4.name, 'O', rg_m3m4)
    i5_en_xy = laygen.get_inst_pin_xy(i5.name, 'EN', rg_m3m4)
    i5_i_xy = laygen.get_inst_pin_xy(i5.name, 'I', rg_m3m4)
    i5_o_xy = laygen.get_inst_pin_xy(i5.name, 'O', rg_m3m4)

    #reference route coordinate
    y0 = i3_i_xy[0][1]
    x0 = laygen.get_xy(obj =it0, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_xy(obj =i5, gridname=rg_m3m4)[0]\
         +laygen.get_xy(obj =i5.template, gridname=rg_m3m4)[0] - 1
    #en
    rv0, ren0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i3_en_xy[0], np.array([x0, y0+1 - 4]), rg_m3m4)
    rv0, ren1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i4_en_xy[0], np.array([x0, y0+1 - 3]), rg_m3m4)
    rv0, ren2 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i5_en_xy[0], np.array([x0, y0+1 - 2]), rg_m3m4)

    #shield
    rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], it0_vdd_xy[0], np.array([x0, y0+1 - 1]), rg_m3m4)
    rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], it0_vdd_xy[0], np.array([x1, y0+1 - 1]), rg_m3m4)
    rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], it0_vdd_xy[0], np.array([x0, y0 + 7]), rg_m3m4)
    rv0, rh0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], it0_vdd_xy[0], np.array([x1, y0 + 7]), rg_m3m4)

    #vref
    for i in range(int(m/2)):
        rv0, rvref0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i3_i_xy[0]+np.array([2*i, 0]), np.array([x0, y0+1 + 0]), rg_m3m4)
        rv0, rvref1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i4_i_xy[0]+np.array([2*i, 0]), np.array([x0, y0 + 2]), rg_m3m4)
        rv0, rvref2 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i5_i_xy[0]+np.array([2*i, 0]), np.array([x0, y0 + 4]), rg_m3m4)

    #out
    for i in range(int(m/2)):
        rv0, rvo0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i3_o_xy[0]+np.array([2*i, 0]), np.array([x1, y0 + 6]), rg_m3m4)
        rv0, rvo1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i4_o_xy[0]+np.array([2*i, 0]), np.array([x1, y0 + 6]), rg_m3m4)
        rv0, rvo2 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], i5_o_xy[0]+np.array([2*i, 0]), np.array([x1, y0 + 6]), rg_m3m4)

    #pin
    laygen.boundary_pin_from_rect(ren0, rg_m3m4, "EN<0>", laygen.layers['pin'][4], size=4, direction='left')
    laygen.boundary_pin_from_rect(ren1, rg_m3m4, "EN<1>", laygen.layers['pin'][4], size=4, direction='left')
    laygen.boundary_pin_from_rect(ren2, rg_m3m4, "EN<2>", laygen.layers['pin'][4], size=4, direction='left')
    laygen.boundary_pin_from_rect(rvref0, rg_m3m4, "VREF<0>", laygen.layers['pin'][4], size=4, direction='left')
    laygen.boundary_pin_from_rect(rvref1, rg_m3m4, "VREF<1>", laygen.layers['pin'][4], size=4, direction='left')
    laygen.boundary_pin_from_rect(rvref2, rg_m3m4, "VREF<2>", laygen.layers['pin'][4], size=4, direction='left')
    laygen.boundary_pin_from_rect(rvo0, rg_m3m4, "VO", laygen.layers['pin'][4], size=4, direction='right')

    # power pin
    inst_left=it0
    inst_right=refi
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS1', rg_m1m2, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS1', rg_m1m2, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS0', rg_m1m2, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS0', rg_m1m2, sort=True)

    laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=rg_m1m2, netname='VSS')
    laygen.pin(name='VSS0', layer=laygen.layers['pin'][2], xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=rg_m1m2, netname='VSS')

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

    # library load or generation
    workinglib = 'adc_sar_generated'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    if os.path.exists(workinglib + '.yaml'):  # generated layout file exists
        laygen.load_template(filename=workinglib + '.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #grid
    pg = 'placement_basic' #placement grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m1m2_thick = 'route_M1_M2_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m2m3_thick = 'route_M2_M3_thick_basic'
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
    m_list = [2,4,8]
    m_space_offset = 0
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        m_list=list(set(sizedict['capdrv']['m_list']))
        m_space_offset=sizedict['capdrv']['space_offset']
        num_bits=specdict['n_bit']
    m_space_ref=max(m_list+[8])
    #capdrv generation
    for m in m_list:
        cellname='capdrv_nsw_'+str(m)+'x'
        print(cellname+" generating")
        mycell_list.append(cellname)
        laygen.add_cell(cellname)
        laygen.sel_cell(cellname)
        generate_capdrv_nsw(laygen, objectname_pfix='CD0', templib_logic=logictemplib,
                            placement_grid=pg, routing_grid_m3m4=rg_m3m4, m=m, m_space=max(0, num_bits-8)*2+3*(m_space_ref-m)+m_space_offset, origin=np.array([0, 0]))
                            #m_space multiplied by 3 because of 3 references
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
