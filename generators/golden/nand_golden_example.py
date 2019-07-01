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

"""Logic layout
"""
import laygo
import numpy as np
import os
#import logging;logging.basicConfig(level=logging.DEBUG)

def create_io_pin(laygen, layer, gridname, pinname_list, rect_list, offset_y=np.array([-1, 1])):
    """create digital io pin"""
    rect_xy_list = [laygen.get_rect_xy(name=r.name, gridname=gridname, sort=True) for r in rect_list]
    #align pin shapes
    ry = rect_xy_list[0][:, 1] + offset_y.T
    for i, xy_rect in enumerate(rect_xy_list):
        xy_rect[:, 1]=ry
        laygen.pin(name=pinname_list[i], layer=layer, xy=xy_rect, gridname=gridname)

def create_power_pin(laygen, layer, gridname, rect_vdd, rect_vss, pinname_vdd='VDD', pinname_vss='VSS'):
    """create power pin"""
    rvdd_pin_xy = laygen.get_rect_xy(rect_vdd.name, gridname)
    rvss_pin_xy = laygen.get_rect_xy(rect_vss.name, gridname)
    laygen.pin(name=pinname_vdd, layer=layer, xy=rvdd_pin_xy, gridname=gridname)
    laygen.pin(name=pinname_vss, layer=layer, xy=rvss_pin_xy, gridname=gridname)

def generate_nand(laygen, prefix, placement_grid, routing_grid_m1m2, routing_grid_m2m3, routing_grid_m3m4,
                  devname_nmos_boundary, devname_nmos_body, devname_pmos_boundary, devname_pmos_body,
                  m=2, origin=[0, 0], create_pin=False):
    """generate nand gate layout"""
    pg = placement_grid
    rg12 = routing_grid_m1m2
    rg23 = routing_grid_m2m3
    rg34 = routing_grid_m3m4

    _m=m
    if m==1:
        m=1                #use nf=1 devices (not implemented yet)
    else:
        m=max(1, int(m/2)) #use nf=2 devices

    # placement
    nrow = laygen.relplace(name=['I'+prefix+'N'+str(i) for i in range(6)],
                           templatename=[devname_nmos_boundary, devname_nmos_body, devname_nmos_boundary,
                                         devname_nmos_boundary, devname_nmos_body, devname_nmos_boundary], 
                           gridname=pg, refobj=None, direction=['right']*6, 
                           shape=[[1, 1], [m, 1], [1, 1]]*2, transform='R0')
    prow = laygen.relplace(name=['I'+prefix+'P'+str(i) for i in range(6)], 
                           templatename=[devname_pmos_boundary, devname_pmos_body, devname_pmos_boundary,
                                         devname_pmos_boundary, devname_pmos_body, devname_pmos_boundary],
                           gridname=pg, refobj=nrow[0], direction=['top']+['right']*5, 
                           shape=[[1, 1], [m, 1], [1, 1]]*2, transform='MX')
    nd=[nrow[1].elements[:,0], nrow[4].elements[:,0]]
    pd=[prow[1].elements[:,0], prow[4].elements[:,0]]

    # route
    if m == 1: 
        rofst=[-1, 1]
        rend='extend'
    else: 
        rofst=[0, 0]
        rend='truncate'
    # b-metal1
    for _nd, _pd in zip(nd[0], pd[0]):
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=_nd.pins['G0'], refobj1=_pd.pins['G0'], via0=[0, 0])
    # b-metal2
    laygen.route(name=None, xy0=[rofst[0], 0], xy1=[rofst[1], 0], gridname0=rg23, refobj0=nd[0][0].pins['G0'], 
                 refobj1=nd[0][-1].pins['G0'], endstyle0=rend, endstyle1=rend)
    # b-metal3
    rb0 = laygen.route(name=None, xy0=[rofst[0], 0], xy1=[rofst[0], 2], gridname0=rg23, refobj0=nd[0][0].pins['G0'], 
                       refobj1=nd[0][0].pins['G0'], via0=[0, 0])
    # a
    for _nd, _pd in zip(nd[1], pd[1]):
        laygen.route(name=None, xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=_nd.pins['G0'], refobj1=_pd.pins['G0'], via1=[0, 0])
    laygen.route(name=None, xy0=[rofst[0], 0], xy1=[rofst[1], 0], gridname0=rg23, refobj0=pd[1][0].pins['G0'], 
                 refobj1=pd[1][-1].pins['G0'], endstyle0=rend, endstyle1=rend)
    ra0 = laygen.route(name=None, xy0=[rofst[0], 0], xy1=[rofst[0], 2], gridname0=rg23, refobj0=pd[1][0].pins['G0'], 
                       refobj1=pd[1][0].pins['G0'], via0=[0, 0])
    # internal connections
    laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg23, refobj0=nd[0][0].pins['D0'], refobj1=nd[1][-1].pins['S1'])
    laygen.route(name=None, xy0=[0, 1], xy1=[0, 1], gridname0=rg23, refobj0=pd[0][0].pins['D0'], refobj1=pd[1][-1].pins['D0'])
    for dev, pn in zip([nd[0], pd[0], nd[1], pd[1]], ['D0', 'D0', 'S0', 'D0']):
        for _d in dev:
            laygen.via(None, xy=[0, 1], refobj=_d.pins[pn], gridname=rg12)
    laygen.via(None, xy=[0, 1], refobj=nd[1][-1].pins['S1'], gridname=rg12)
    # output
    laygen.route(name=None, xy0=[rofst[0], 0], xy1=[rofst[1], 0], gridname0=rg23, refobj0=nd[1][0].pins['D0'], 
                 refobj1=nd[1][-1].pins['D0'], endstyle0=rend, endstyle1=rend)
    for _nd in nd[1]:
        laygen.via(None, xy=[0, 0], refobj=_nd.pins['D0'], gridname=rg12)
    ro0 = laygen.route(name=None, xy0=[0, 0], xy1=[0, 1], gridname0=rg23, refobj0=nd[1][-1].pins['D0'], 
                       refobj1=pd[1][-1].pins['D0'], via0=[0, 0], via1=[0, 0])
    # power and ground route
    xy_s0 = laygen.get_template_pin_xy(name=nrow[1].cellname, pinname='S0', gridname=rg12)[0, :]
    xy_s1 = laygen.get_template_pin_xy(name=nrow[1].cellname, pinname='S1', gridname=rg12)[0, :]
    for dev in np.concatenate((nd[0],pd[0],pd[1])):
        for xy in [xy_s0, xy_s1]:
            for i in range(m):
                laygen.route(name=None, xy0=[xy[0], 0], xy1=xy, gridname0=rg12, refobj0=dev, refobj1=dev, via0=[0, 0])
    # power and groud rail
    xy = laygen.get_template_xy(nrow[5].cellname, rg12) * np.array([1, 0])
    rvdd=laygen.route(name='R'+prefix+'VDD0', xy0=[0, 0], xy1=xy, gridname0=rg12, refobj0=prow[0], refobj1=prow[5])
    rvss=laygen.route(name='R'+prefix+'VSS0', xy0=[0, 0], xy1=xy, gridname0=rg12, refobj0=nrow[0], refobj1=nrow[5])

    # pin
    if create_pin == True:
        create_io_pin(laygen, layer=laygen.layers['pin'][3], gridname=rg34,
                      pinname_list = ['A', 'B', 'O'], rect_list=[ra0, rb0, ro0])
        create_power_pin(laygen, layer=laygen.layers['pin'][2], gridname=rg12, rect_vdd=rvdd, rect_vss=rvss)

if __name__ == '__main__':
    # initialize #######################################################################################################
    import imp
    try:
        imp.find_module('bag')
        lib_path = ''
        laygen = laygo.GridLayoutGenerator(config_file=lib_path+"laygo_config.yaml")
        use_phantom = False
    except ImportError:
        # if bag does not exist, load faketech lib and export phantom to gds
        lib_path = '../../labs/'
        use_phantom = True
    laygen = laygo.GridLayoutGenerator(config_file=lib_path + "laygo_config.yaml")
    laygen.use_phantom = use_phantom

    # template and grid load
    utemplib = laygen.tech + '_microtemplates_dense'  # device template library name
    laygen.load_template(filename=lib_path + utemplib + '_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=lib_path + utemplib + '_grids.yaml', libname=utemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    # generate a library and cell to work on
    workinglib = 'laygo_working'
    laygen.add_library(workinglib)
    if os.path.exists(workinglib+'.yaml'): #generated template library exists
        laygen.load_template(filename=workinglib+'.yaml', libname=workinglib)
        laygen.templates.sel_library(utemplib)

    # parameters
    pg = 'placement_basic' # placement grid
    rg12 = 'route_M1_M2_cmos' #route grids
    rg23 = 'route_M2_M3_cmos'
    rg34 = 'route_M3_M4_basic'
    nb = 'nmos4_fast_boundary'  # nmos boundary cellname
    nc = 'nmos4_fast_center_nf2'  # nmos body cellname
    pb = 'pmos4_fast_boundary'  # pmos boundary cellname
    pc = 'pmos4_fast_center_nf2'  # pmos body cellname

    # cell generation
    mycell_dict = {'nand': [2, 4, 8, 16]}
    mycell_list=[]
    for mc in mycell_dict:
        for m in mycell_dict[mc]:
            cellname=mc+'_'+str(m)+'x'
            mycell_list.append(cellname)
            laygen.add_cell(cellname)
            laygen.sel_cell(cellname)
            generate_nand(laygen, prefix='ND0', 
                          placement_grid=pg, 
                          routing_grid_m1m2=rg12,
                          routing_grid_m2m3=rg23, 
                          routing_grid_m3m4=rg34, 
                          devname_nmos_boundary=nb,
                          devname_nmos_body=nc,
                          devname_pmos_boundary=pb,
                          devname_pmos_body=pc,
                          m=m, create_pin=True)
            laygen.add_template_from_cell()

    #save template database to file
    laygen.save_template(filename=workinglib+'.yaml', libname=workinglib)

    # export ###########################################################################################################
    # bag export, if bag does not exist, gds export
    import imp
    try:
        imp.find_module('bag')
        import bag

        prj = bag.BagProject()
        for mycell in mycell_list:
            laygen.sel_cell(mycell)
            laygen.export_BAG(prj, array_delimiter=['[', ']'])
    except ImportError:
        laygen.export_GDS('output.gds', cellname=mycell_list,
                          layermapfile=lib_path + "laygo_faketech.layermap")  # change layermapfile
