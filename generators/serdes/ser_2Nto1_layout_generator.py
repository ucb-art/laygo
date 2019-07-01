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

"""SER library
"""
import laygo
import numpy as np
#from logic_layout_generator import *
from math import log
import yaml
import os
#import logging;logging.basicConfig(level=logging.DEBUG)

def generate_serializer(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m2m3,
                          routing_grid_m4m5, num_ser=8, m_ser=1, origin=np.array([0, 0])):
    pg = placement_grid

    rg_m2m3 = routing_grid_m2m3
    rg_m4m5 = routing_grid_m4m5

    sub_ser = int(num_ser/2)
    subser_name = 'ser_'+str(sub_ser)+'to1'
    ser2to1_name = 'ser_2to1_halfrate'
    # placement
    isubser0=laygen.place(name = "I" + objectname_pfix + 'SSER0', templatename = subser_name,
            gridname = pg, xy=origin, transform="R0", shape=np.array([1,1]), template_libname = workinglib)
    iser2to1=laygen.relplace(name = "I" + objectname_pfix + 'SER2to1', templatename = ser2to1_name,
            gridname = pg, refinstname = isubser0.name, transform="R0", shape=np.array([1,1]), template_libname = workinglib, direction = 'top')
    isubser1=laygen.relplace(name = "I" + objectname_pfix + 'SSER1', templatename = subser_name,
            gridname = pg, refinstname = iser2to1.name, transform="MX", shape=np.array([1,1]), template_libname = workinglib, direction = 'top')

    #Internal Pins
    subser0_out_xy=laygen.get_inst_pin_xy(isubser0.name, 'out', rg_m3m4)
    subser0_rst_xy=laygen.get_inst_pin_xy(isubser0.name, 'RST', rg_m3m4)
    subser0_clk_xy=laygen.get_inst_pin_xy(isubser0.name, 'clk_in', rg_m3m4)
    subser1_out_xy=laygen.get_inst_pin_xy(isubser1.name, 'out', rg_m3m4)
    subser1_rst_xy=laygen.get_inst_pin_xy(isubser1.name, 'RST', rg_m3m4)
    subser1_clk_xy=laygen.get_inst_pin_xy(isubser1.name, 'clk_in', rg_m3m4)
    ser2to1_clkb_xy=laygen.get_inst_pin_xy(iser2to1.name, 'CLKB', rg_m3m4)
    ser2to1_clk_xy=laygen.get_inst_pin_xy(iser2to1.name, 'CLK', rg_m3m4)
    ser2to1_i1_xy=laygen.get_inst_pin_xy(iser2to1.name, 'I<1>', rg_m3m4)
    ser2to1_i0_xy=laygen.get_inst_pin_xy(iser2to1.name, 'I<0>', rg_m3m4)
    ser2to1_out_xy=laygen.get_inst_pin_xy(iser2to1.name, 'O', rg_m3m4)
    divclk_xy=laygen.get_inst_pin_xy(isubser0.name, 'p1buf', rg_m3m4)

    # Route
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                subser0_out_xy[0], ser2to1_i0_xy[0], subser0_out_xy[0][1]+5, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], 
                subser1_out_xy[0], ser2to1_i1_xy[1], subser1_out_xy[0][1]-5, rg_m3m4)
    [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][3], 
                ser2to1_clk_xy[0], subser0_clk_xy[1], subser0_clk_xy[1][0], rg_m3m4)
    [rh0, rv0, rh1] = laygen.route_hvh(laygen.layers['metal'][4], laygen.layers['metal'][3], 
                ser2to1_clk_xy[1], subser1_clk_xy[1], subser1_clk_xy[1][0], rg_m3m4)

    #Pin
    laygen.pin(name='CLK', layer=laygen.layers['pin'][4], xy=ser2to1_clk_xy, gridname=rg_m3m4)
    laygen.pin(name='CLKB', layer=laygen.layers['pin'][4], xy=ser2to1_clkb_xy, gridname=rg_m3m4)
    laygen.pin(name='out', layer=laygen.layers['pin'][4], xy=ser2to1_out_xy, gridname=rg_m3m4)
    laygen.pin(name='divclk', layer=laygen.layers['pin'][3], xy=divclk_xy, gridname=rg_m3m4)
    laygen.pin(name='RST0', layer=laygen.layers['pin'][3], xy=subser0_rst_xy, netname='RST:', gridname=rg_m3m4)
    laygen.pin(name='RST1', layer=laygen.layers['pin'][3], xy=subser1_rst_xy, netname='RST:', gridname=rg_m3m4)

    for i in range(sub_ser):
        subser0_in_xy=laygen.get_inst_pin_xy(isubser0.name, 'in<' + str(i) + '>', rg_m3m4)
        laygen.pin(name='in<'+str(2*i)+'>', layer=laygen.layers['pin'][4], xy=subser0_in_xy, gridname=rg_m3m4)
        subser1_in_xy=laygen.get_inst_pin_xy(isubser1.name, 'in<' + str(i) + '>', rg_m3m4)
        laygen.pin(name='in<'+str(2*i+1)+'>', layer=laygen.layers['pin'][4], xy=subser1_in_xy, gridname=rg_m3m4)

    # power pin
    pwr_dim=laygen.get_xy(obj=laygen.get_template(name='tap', libname=logictemplib), gridname=rg_m2m3)
    rvdd = []
    rvss = []
    print(int(pwr_dim[0]))
    for i in range(-2, int(pwr_dim[0]/2)*2-2):
        subser0_vdd_xy=laygen.get_inst_pin_xy(isubser0.name, 'VDD' + str(i), rg_m2m3)
        subser0_vss_xy=laygen.get_inst_pin_xy(isubser0.name, 'VSS' + str(i), rg_m2m3)
        subser1_vdd_xy=laygen.get_inst_pin_xy(isubser1.name, 'VDD' + str(i), rg_m2m3)
        subser1_vss_xy=laygen.get_inst_pin_xy(isubser1.name, 'VSS' + str(i), rg_m2m3)
        rvdd.append(laygen.route(None, laygen.layers['metal'][3], xy0=subser0_vdd_xy[0], xy1=subser1_vdd_xy[0], gridname0=rg_m2m3))
        rvss.append(laygen.route(None, laygen.layers['metal'][3], xy0=subser0_vss_xy[0], xy1=subser1_vss_xy[0], gridname0=rg_m2m3))
        laygen.pin(name = 'VDD'+str(i), layer = laygen.layers['pin'][3], refobj = rvdd[-1], gridname=rg_m2m3, netname='VDD')
        laygen.pin(name = 'VSS'+str(i), layer = laygen.layers['pin'][3], refobj = rvss[-1], gridname=rg_m2m3, netname='VSS')

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
    workinglib = 'serdes_generated'
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
    
    #load from preset
    load_from_file=True
    yamlfile_spec="serdes_spec.yaml"
    yamlfile_size="serdes_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        cell_name='ser_2Nto1_'+str(int(specdict['num_ser']))+'to1'
        num_ser=specdict['num_ser']
        m_ser=sizedict['m_ser']

    print(cell_name+" generating")
    mycell_list.append(cell_name)
    laygen.add_cell(cell_name)
    laygen.sel_cell(cell_name)
    generate_serializer(laygen, objectname_pfix='SER', templib_logic=logictemplib, 
                          placement_grid=pg, routing_grid_m2m3=rg_m2m3, routing_grid_m4m5=rg_m4m5, num_ser=num_ser,
                          m_ser=m_ser, origin=np.array([0, 0]))
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
