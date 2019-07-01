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

def create_power_pin_from_inst(laygen, layer, gridname, inst_left, inst_right):
    """create power pin"""
    rvdd0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VDD', gridname, sort=True)
    rvdd1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VDD', gridname, sort=True)
    rvss0_pin_xy = laygen.get_inst_pin_xy(inst_left.name, 'VSS', gridname, sort=True)
    rvss1_pin_xy = laygen.get_inst_pin_xy(inst_right.name, 'VSS', gridname, sort=True)

    laygen.pin(name='VDD', layer=layer, xy=np.vstack((rvdd0_pin_xy[0],rvdd1_pin_xy[1])), gridname=gridname)
    laygen.pin(name='VSS', layer=layer, xy=np.vstack((rvss0_pin_xy[0],rvss1_pin_xy[1])), gridname=gridname)

def generate_capsw_array(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4, num_bits, m, origin=np.array([0, 0])):
    """generate cap driver """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    m = max(1, int(m / 2))  # using nf=2 devices

    isp_cell = []
    capsw_cell = []

    isp=laygen.place(name="I" + objectname_pfix + 'SP1X0', templatename='space_1x',
                     gridname=pg, xy=origin, template_libname=templib_logic) 
    isp_cell.append(isp)

    for num in range(num_bits):
        capsw = laygen.relplace(name="I" + objectname_pfix +'CAPSW'+str(num), templatename='cap_sw_'+str(m*2**(num+1))+'x',
                        gridname=pg, refinstname = isp.name, template_libname=templib_logic)
        isp = laygen.relplace(name="I" + objectname_pfix +'SP1X'+str(num+1), templatename='space_1x',
                        gridname=pg, refinstname = capsw.name, template_libname=templib_logic)
        capsw_cell.append(capsw)
        isp_cell.append(isp)
        
    
    # internal pins
    isp_cell_pin = []
    capsw_cell_pin_en = []
    capsw_cell_pin_vo = []
    for num in range(num_bits):
        capsw_pin_xy = laygen.get_inst_pin_xy(capsw_cell[num].name, 'EN', rg_m3m4)
        capsw_cell_pin_en.append(capsw_pin_xy)
        capsw_pin_xy = laygen.get_inst_pin_xy(capsw_cell[num].name, 'VO', rg_m3m4)
        capsw_cell_pin_vo.append(capsw_pin_xy)
    
    #pin
    for num in range(num_bits):
        laygen.pin(name='EN<'+str(num)+'>', layer=laygen.layers['pin'][3], xy=capsw_cell_pin_en[num], gridname=rg_m3m4)
        for i in range(num_bits):
            laygen.pin(name='VO<'+str(num)+'>', layer=laygen.layers['pin'][3], xy=capsw_cell_pin_vo[num], gridname=rg_m3m4)
        
    # power pin
    ##get left and right side coodinate
    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=isp_cell[0], inst_right=isp_cell[num_bits])
    

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
    workinglib = 'clk_dis_generated'
    laygen.add_library(workinglib)
    laygen.sel_library(workinglib)
    if os.path.exists(workinglib + '.yaml'):  # generated layout file exists
        laygen.load_template(filename=workinglib + '.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    #grid
    pg = 'placement_basic' #placement grid
    rg_m1m2 = 'route_M1_M2_cmos'
    rg_m1m2_thick = 'route_M1_M2_basic_thick'
    rg_m2m3 = 'route_M2_M3_cmos'
    rg_m2m3_thick = 'route_M2_M3_thick'
    rg_m3m4 = 'route_M3_M4_basic'
    rg_m4m5 = 'route_M4_M5_basic'
    rg_m5m6 = 'route_M5_M6_basic'
    rg_m1m2_pin = 'route_M1_M2_basic'
    rg_m2m3_pin = 'route_M2_M3_basic'

    #display
    #laygen.display()
    #laygen.templates.display()
    #laygen.save_template(filename=workinglib+'.yaml', libname=workinglib)

    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        num_bits = sizedict['clk_dis_cdac']['num_bits']
        m_capsw = sizedict['clk_dis_capsw']['m']

    mycell_list = []
    m_list = [num_bits]
    #capdrv generation
    for num in m_list:
        cellname='cap_sw_array'
        print(cellname+" generating")
        mycell_list.append(cellname)
        laygen.add_cell(cellname)
        laygen.sel_cell(cellname)
        generate_capsw_array(laygen, objectname_pfix='CD0', templib_logic=logictemplib,
                            placement_grid=pg, routing_grid_m3m4=rg_m3m4, num_bits=num, m=m_capsw, origin=np.array([0, 0]))
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
