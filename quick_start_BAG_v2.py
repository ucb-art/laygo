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
    laygen = laygo.GridLayoutGenerator2(config_file="laygo_config.yaml")
    #template and grid load
    utemplib = laygen.tech+'_microtemplates_dense' #device template library name
    laygen.load_template(filename=utemplib+'_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=utemplib+'_grids.yaml', libname=utemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    # library & cell creation
    laygen.add_library('laygo_working')
    laygen.add_cell('nand_demo')

    # placement ########################################################################################################
    # placement parameters
    pg = 'placement_basic'  # placement grid

    nd = [] # nmos
    nd += [laygen.place(gridname=pg, cellname='nmos4_fast_boundary')]
    nd += [laygen.place(gridname=pg, cellname='nmos4_fast_center_nf2', ref=nd[-1].right, shape=[2, 1])]
    nd += [laygen.place(gridname=pg, cellname='nmos4_fast_boundary', ref=nd[-1].right)]
    nd += [laygen.place(gridname=pg, cellname='nmos4_fast_boundary', ref=nd[-1].right)]
    nd += [laygen.place(gridname=pg, cellname='nmos4_fast_center_nf2', ref=nd[-1].right, shape=[2, 1])]
    nd += [laygen.place(gridname=pg, cellname='nmos4_fast_boundary', ref=nd[-1].right)]
    pd = []  # pmos
    pd += [laygen.place(gridname=pg, cellname='pmos4_fast_boundary', ref=nd[0].top, transform='MX')]
    pd += [laygen.place(gridname=pg, cellname='pmos4_fast_center_nf2', ref=pd[-1].right, shape=[2, 1], transform='MX')]
    pd += [laygen.place(gridname=pg, cellname='pmos4_fast_boundary', ref=pd[-1].right, transform='MX')]
    pd += [laygen.place(gridname=pg, cellname='pmos4_fast_boundary', ref=pd[-1].right, transform='MX')]
    pd += [laygen.place(gridname=pg, cellname='pmos4_fast_center_nf2', ref=pd[-1].right, shape=[2, 1], transform='MX')]
    pd += [laygen.place(gridname=pg, cellname='pmos4_fast_boundary', ref=pd[-1].right, transform='MX')]

    # route ############################################################################################################
    # route parameters
    rg12 = 'route_M1_M2_cmos'  # grids
    rg23 = 'route_M2_M3_cmos'
    # a
    r0 = laygen.route(gridname0=rg12, ref0=nd[4].pins['G0'], ref1=pd[4].pins['G0'], via1=[0, 0])
    r1 = laygen.route(gridname0=rg12, mn0=[0, 0], mn1=[0, 0], ref0=pd[4].pins['G0'][0, 0], ref1=pd[4].pins['G0'][-1, 0])
    ra = laygen.route(gridname0=rg23, mn0=[0, 0], mn1=[0, 2], ref0=pd[4].pins['G0'][0, 0], ref1=pd[4].pins['G0'][0, 0], via0=[0, 0])
    # b
    laygen.route(gridname0=rg12, ref0=nd[1].pins['G0'], ref1=pd[1].pins['G0'], via0=[0, 0])
    laygen.route(gridname0=rg12, mn0=[0, 0], mn1=[0, 0], ref0=nd[1].pins['G0'][0, 0], ref1=nd[1].pins['G0'][-1, 0])
    rb = laygen.route(gridname0=rg23, mn0=[0, 0], mn1=[0, 2], ref0=nd[1].pins['G0'][0, 0], ref1=nd[1].pins['G0'][0, 0], via0=[0, 0])
    # internal connections
    ri = laygen.route(gridname0=rg12, ref0=nd[1].pins['D0'][0, 0].top, ref1=nd[4].pins['S1'][-1, 0].top)
    for _p in np.concatenate((nd[1].pins['D0'], nd[4].pins['S0'], nd[4].pins['S1'])):
        laygen.via(gridname=rg12, ref=_p, overlay=ri)
    # output
    ron = laygen.route(gridname0=rg12, mn0=[-1, 0], mn1=[1, 0], ref0=nd[4].pins['D0'][0, 0], ref1=nd[4].pins['D0'][-1, 0])
    rop = laygen.route(gridname0=rg12, mn0=[0, 0], mn1=[1, 0], ref0=pd[1].pins['D0'][0, 0].top, ref1=pd[4].pins['D0'][-1, 0].top)
    laygen.via(gridname=rg12, ref=nd[4].pins['D0'], overlay=ron)
    laygen.via(gridname=rg12, ref=pd[1].pins['D0'], overlay=rop)
    laygen.via(gridname=rg12, ref=pd[4].pins['D0'], overlay=rop)
    ro = laygen.route(gridname0=rg23, ref0=ron.right, ref1=rop.right, via0=[0, 0], via1=[0, 0])
    # power and ground route
    for dev in [nd[1], pd[1], pd[4]]:
        for pn in ['S0', 'S1']:
            laygen.route(gridname0=rg12, ref0=dev.pins[pn], ref1=dev.bottom, direction='y', via1=[0, 0])
    # power and groud rails
    rvdd = laygen.route(gridname0=rg12, ref0=pd[0].bottom_left, ref1=pd[5].bottom_right)
    rvss = laygen.route(gridname0=rg12, ref0=nd[0].bottom_left, ref1=nd[5].bottom_right)

    # pin ##############################################################################################################
    for pn, pg, pr in zip(['A', 'B', 'O', 'VDD', 'VSS'], [rg12, rg12, rg23, rg12, rg12], [ra, rb, ro, rvdd, rvss]):
        laygen.pin(name=pn, gridname=pg, ref=pr)

    # display ##########################################################################################################
    laygen.display()
    # export
    import bag
    prj = bag.BagProject()
    laygen.export_BAG(prj)

