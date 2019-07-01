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

"""Quick start script for bag flow - nand gate layout generator"""
__author__ = "Jaeduk Han"
__maintainer__ = "Jaeduk Han"
__email__ = "jdhan@eecs.berkeley.edu"
__status__ = "Prototype"

if __name__ == '__main__':
    import laygo
    import numpy as np

    # initialize #######################################################################################################
    laygen = laygo.GridLayoutGenerator(config_file="./labs/laygo_config.yaml")
    laygen.use_phantom = True  # for abstract generation. False when generating a real layout.
    laygen.use_array = True  # use InstanceArray instead of Instance
    # load template and grid
    utemplib = laygen.tech + '_microtemplates_dense'  # device template library name
    laygen.load_template(filename='./labs/' + utemplib + '_templates.yaml', libname=utemplib)
    laygen.load_grid(filename='./labs/' + utemplib + '_grids.yaml', libname=utemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    # library & cell creation
    laygen.add_library('laygo_working')
    laygen.add_cell('nand_demo')

    # placement ########################################################################################################
    # placement parameters
    pg = 'placement_basic'  # placement grid

    nd = [] # nmos
    nd += [laygen.relplace(cellname='nmos4_fast_boundary', gridname=pg, refobj=None, shape=None)]
    nd += [laygen.relplace(cellname='nmos4_fast_center_nf2', gridname=pg, refobj=nd[-1].right, shape=[1, 1])]
    nd += [laygen.relplace(cellname='nmos4_fast_boundary', gridname=pg, refobj=nd[-1].right, shape=None)]
    nd += [laygen.relplace(cellname='nmos4_fast_boundary', gridname=pg, refobj=nd[-1].right, shape=None)]
    nd += [laygen.relplace(cellname='nmos4_fast_center_nf2', gridname=pg, refobj=nd[-1].right, shape=[1, 1])]
    nd += [laygen.relplace(cellname='nmos4_fast_boundary', gridname=pg, refobj=nd[-1].right, shape=None)]
    pd = [] # pmos
    pd += [laygen.relplace(cellname='pmos4_fast_boundary', gridname=pg, refobj=nd[0].top, shape=None, transform='MX')]
    pd += [laygen.relplace(cellname='pmos4_fast_center_nf2', gridname=pg, refobj=pd[-1].right, shape=[1, 1], transform='MX')]
    pd += [laygen.relplace(cellname='pmos4_fast_boundary', gridname=pg, refobj=pd[-1].right, shape=None, transform='MX')]
    pd += [laygen.relplace(cellname='pmos4_fast_boundary', gridname=pg, refobj=pd[-1].right, shape=None, transform='MX')]
    pd += [laygen.relplace(cellname='pmos4_fast_center_nf2', gridname=pg, refobj=pd[-1].right, shape=[1, 1], transform='MX')]
    pd += [laygen.relplace(cellname='pmos4_fast_boundary', gridname=pg, refobj=pd[-1].right, shape=None, transform='MX')]

    # route ############################################################################################################
    # route parameters
    rg12 = 'route_M1_M2_cmos'  # grids
    rg23 = 'route_M2_M3_cmos'

    # a
    laygen.route(gridname0=rg12, refobj0=nd[4].pins['G0'], refobj1=pd[4].pins['G0'], via1=[0, 0])
    laygen.route(gridname0=rg12, xy0=[-2, 0], xy1=[0, 0], refobj0=pd[4].pins['G0'][0, 0], refobj1=pd[4].pins['G0'][-1, 0])
    ra = laygen.route(gridname0=rg23, xy0=[0, 0], xy1=[0, 2], refobj0=pd[4].pins['G0'][0, 0], refobj1=pd[4].pins['G0'][0, 0], via0=[0, 0])
    # b
    laygen.route(gridname0=rg12, refobj0=nd[1].pins['G0'], refobj1=pd[1].pins['G0'], via0=[0, 0])
    laygen.route(gridname0=rg12, xy0=[0, 0], xy1=[2, 0], refobj0=nd[1].pins['G0'][0, 0], refobj1=nd[1].pins['G0'][-1, 0])
    rb = laygen.route(gridname0=rg23, xy0=[0, 0], xy1=[0, 2], refobj0=nd[1].pins['G0'][0, 0], refobj1=nd[1].pins['G0'][0, 0], via0=[0, 0])
    # internal connections
    ri = laygen.route(xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=nd[1].pins['D0'][0, 0],
                      refobj1=nd[4].pins['S1'][-1, 0])
    for _p in np.concatenate((nd[1].pins['D0'], nd[4].pins['S0'], nd[4].pins['S1'])):
        laygen.via(xy=[0, 0], refobj=_p, gridname=rg12, overlay=ri)
    # output
    ron = laygen.route(gridname0=rg12, xy0=[-1, 0], xy1=[1, 0], refobj0=nd[4].pins['D0'][0, 0], refobj1=nd[4].pins['D0'][-1, 0])
    rop = laygen.route(gridname0=rg12, xy0=[0, 0], xy1=[1, 0], refobj0=pd[1].pins['D0'][0, 0], refobj1=pd[4].pins['D0'][-1, 0])
    laygen.via(refobj=nd[4].pins['D0'], gridname=rg12, overlay=ron)
    laygen.via(refobj=pd[1].pins['D0'], gridname=rg12, overlay=rop)
    laygen.via(refobj=pd[4].pins['D0'], gridname=rg12, overlay=rop)
    ro = laygen.route(gridname0=rg23, refobj0=ron.right, refobj1=rop.right, xy0=[0, 0], xy1=[0, 0], via0=[0, 0], via1=[0, 0])
    # power and ground route
    for dev in [nd[1], pd[1], pd[4]]:
        for pn in ['S0', 'S1']:
            laygen.route(gridname0=rg12, refobj0=dev.pins[pn], refobj1=dev.bottom, direction='y', via1=[0, 0])
    # power and groud rails
    rvdd = laygen.route(gridname0=rg12, refobj0=pd[0].bottom_left, refobj1=pd[5].bottom_right)
    rvss = laygen.route(gridname0=rg12, refobj0=nd[0].bottom_left, refobj1=nd[5].bottom_right)

    # pin ##############################################################################################################
    for pn, pg, pr in zip(['A', 'B', 'O', 'VDD', 'VSS'], [rg12, rg12, rg23, rg12, rg12], [ra, rb, ro, rvdd, rvss]):
        laygen.pin(name=pn, gridname=pg, refobj=pr)

    # display ##########################################################################################################
    laygen.display()

    # export ###########################################################################################################
    laygen.export_GDS('output.gds', cellname='nand_demo', layermapfile="./labs/laygo_faketech.layermap")

