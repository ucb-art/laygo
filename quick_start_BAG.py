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
    #initialize
    laygen = laygo.GridLayoutGenerator(config_file="laygo_config.yaml")
    #template and grid load
    utemplib = laygen.tech+'_microtemplates_dense' #device template library name
    laygen.load_template(filename=utemplib+'_templates.yaml', libname=utemplib)
    laygen.load_grid(filename=utemplib+'_grids.yaml', libname=utemplib)
    laygen.templates.sel_library(utemplib)
    laygen.grids.sel_library(utemplib)

    # library & cell creation
    laygen.add_library('laygo_working')
    laygen.add_cell('nand_test')

    # grid variables
    pg = 'placement_basic'
    rg12 = 'route_M1_M2_cmos'
    rg23 = 'route_M2_M3_cmos'

    #placements
    nr = ['nmos4_fast_boundary', 'nmos4_fast_center_nf2', 'nmos4_fast_boundary',
          'nmos4_fast_boundary', 'nmos4_fast_center_nf2', 'nmos4_fast_boundary']
    pr = ['pmos4_fast_boundary', 'pmos4_fast_center_nf2', 'pmos4_fast_boundary',
          'pmos4_fast_boundary', 'pmos4_fast_center_nf2', 'pmos4_fast_boundary']
    pd = ['top']+['right']*5
    nrow = laygen.relplace(templatename=nr, gridname=pg)
    prow = laygen.relplace(templatename=pr, gridname=pg, refobj=nrow[0], direction=pd, transform='MX')
    #routes
    #   a
    laygen.route(xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=prow[4].pins['G0'], refobj1=nrow[4].pins['G0'], via0=[0, 0])
    laygen.route(xy0=[-2, 0], xy1=[0, 0], gridname0=rg12, refobj0=prow[4].pins['G0'], refobj1=prow[4].pins['G0'])
    ra0 = laygen.route(xy0=[0, 0], xy1=[0, 2], gridname0=rg23, refobj0=prow[4].pins['G0'], refobj1=prow[4].pins['G0'],
                       via0=[0, 0], endstyle0="extend", endstyle1="extend")
    #   b
    laygen.route(xy0=[0, 0], xy1=[0, 0], gridname0=rg12, refobj0=nrow[1].pins['G0'], refobj1=prow[1].pins['G0'], via0=[0, 0])
    laygen.route(xy0=[0, 0], xy1=[2, 0], gridname0=rg12, refobj0=nrow[1].pins['G0'], refobj1=nrow[1].pins['G0'])
    rb0 = laygen.route(xy0=[0, 0], xy1=[0, 2], gridname0=rg23, refobj0=nrow[1].pins['G0'], refobj1=nrow[1].pins['G0'],
                       via0=[0, 0], endstyle0="extend", endstyle1="extend")
    #   internal
    laygen.route(xy0=[0, 1], xy1=[0, 1], gridname0=rg12, refobj0=nrow[1].pins['D0'], refobj1=nrow[4].pins['S1'],
                 via0=[0, 0], via1=[[-2, 0], [0, 0]])
    #   output
    laygen.route(xy0=[0, 1], xy1=[1, 1], gridname0=rg12, refobj0=prow[1].pins['D0'], refobj1=prow[4].pins['D0'],
                 via0=[0, 0], via1=[-1, 0])
    laygen.route(xy0=[-1, 0], xy1=[1, 0], gridname0=rg12, refobj0=nrow[4].pins['D0'], refobj1=nrow[4].pins['D0'], via0=[1, 0])
    ro0 = laygen.route(xy0=[1, 0], xy1=[1, 1], gridname0=rg23, refobj0=nrow[4].pins['D0'], via0=[0, 0],
                       refobj1=prow[4].pins['D0'], via1=[0, 0])
    #   power and ground route - vertical
    for d in [nrow[1], prow[1], prow[4]]:
        for s in ['S0', 'S1']:
            laygen.route(None, gridname0=rg12, refobj0=d.pins[s], refobj1=d, via1=[0, 0], direction='y')
    #   power and ground route - horizontal
    xy = laygen.get_template_xy(name=nrow[-1].cellname, gridname=rg12) * np.array([1, 0])
    rvdd=laygen.route(None, xy0=[0, 0], xy1=xy, gridname0=rg12, refobj0=prow[0], refobj1=prow[-1])
    rvss=laygen.route(None, xy0=[0, 0], xy1=xy, gridname0=rg12, refobj0=nrow[0], refobj1=nrow[-1])

    #pins
    for pn, rp in zip(['A', 'B', 'O'], [ra0, rb0, ro0]):
        laygen.pin(name=pn, layer=laygen.layers['pin'][3], refobj=rp, gridname=rg23)
    for pn, rp in zip(['VDD', 'VSS'], [rvdd, rvss]):
        laygen.pin(name=pn, layer=laygen.layers['pin'][2], refobj=rp, gridname=rg12)

    laygen.display()
    # export
    import bag
    prj = bag.BagProject()
    laygen.export_BAG(prj)

