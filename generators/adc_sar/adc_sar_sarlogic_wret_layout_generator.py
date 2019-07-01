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

def generate_sarlogic(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4, m=1, origin=np.array([0, 0])):
    """generate sar logic """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    inv_name = 'inv_1x'
    oai22_name = 'oai22_1x'
    mux2to1_name = 'mux2to1_1x'
    nand_name = 'nand_1x'
    nor_name = 'nor_' + str(m) + 'x'
    inv_obuf_name = 'inv_' + str(m) + 'x'
    dff_name = 'dff_1x'
    space_name = 'space_4x'

    # placement
    ioai0 = laygen.place(name = "I" + objectname_pfix + 'OAI0', templatename = oai22_name,
                            gridname = pg, xy=origin, template_libname=templib_logic)
    ildpo0 = laygen.relplace(name="I" + objectname_pfix + 'INV2', templatename=inv_name,
                            gridname=pg, refinstname=ioai0.name, template_libname=templib_logic)
    ioai1 = laygen.relplace(name = "I" + objectname_pfix + 'OAI1', templatename = oai22_name,
                            gridname = pg, refinstname = ildpo0.name, template_libname=templib_logic)
    ildno0 = laygen.relplace(name="I" + objectname_pfix + 'INV3', templatename=inv_name,
                            gridname=pg, refinstname=ioai1.name, template_libname=templib_logic)
    inr0 = laygen.relplace(name="I" + objectname_pfix + 'NR0', templatename=nor_name,
                           gridname=pg, refinstname=ildno0.name, template_libname=templib_logic)
    #ind0 = laygen.relplace(name="I" + objectname_pfix + 'ND0', templatename=nand_name,
    #                       gridname=pg, refinstname=ildno0.name, template_libname=templib_logic)
    izp0 = laygen.relplace(name="I" + objectname_pfix + 'OBUF0', templatename=inv_obuf_name,
                            gridname=pg, refinstname=inr0.name, template_libname=templib_logic)
    izm0 = laygen.relplace(name="I" + objectname_pfix + 'OBUF1', templatename=inv_obuf_name,
                            gridname=pg, refinstname=izp0.name, template_libname=templib_logic)
    #izmid0 = laygen.relplace(name="I" + objectname_pfix + 'OBUF2', templatename=inv_obuf_name,
    #                        gridname=pg, refinstname=izm0.name, template_libname=templib_logic)
    isp0 = laygen.relplace(name="I" + objectname_pfix + 'SP0', templatename=space_name,
                            gridname=pg, refinstname=izm0.name, template_libname=templib_logic)
    idff0 = laygen.relplace(name="I" + objectname_pfix + 'DFF0', templatename=dff_name,
                            gridname=pg, refinstname=isp0.name, template_libname=templib_logic)

    # internal pins
    ioai0_a_xy = laygen.get_inst_pin_xy(ioai0.name, 'A', rg_m3m4)
    ioai0_b_xy = laygen.get_inst_pin_xy(ioai0.name, 'B', rg_m3m4)
    ioai0_c_xy = laygen.get_inst_pin_xy(ioai0.name, 'C', rg_m3m4)
    ioai0_d_xy = laygen.get_inst_pin_xy(ioai0.name, 'D', rg_m3m4)
    ioai0_o_xy = laygen.get_inst_pin_xy(ioai0.name, 'O', rg_m3m4)
    ildpo0_i_xy = laygen.get_inst_pin_xy(ildpo0.name, 'I', rg_m3m4)
    ildpo0_o_xy = laygen.get_inst_pin_xy(ildpo0.name, 'O', rg_m3m4)
    ioai1_a_xy = laygen.get_inst_pin_xy(ioai1.name, 'A', rg_m3m4)
    ioai1_b_xy = laygen.get_inst_pin_xy(ioai1.name, 'B', rg_m3m4)
    ioai1_c_xy = laygen.get_inst_pin_xy(ioai1.name, 'C', rg_m3m4)
    ioai1_d_xy = laygen.get_inst_pin_xy(ioai1.name, 'D', rg_m3m4)
    ioai1_o_xy = laygen.get_inst_pin_xy(ioai1.name, 'O', rg_m3m4)
    ildno0_i_xy = laygen.get_inst_pin_xy(ildno0.name, 'I', rg_m3m4)
    ildno0_o_xy = laygen.get_inst_pin_xy(ildno0.name, 'O', rg_m3m4)
    inr0_a_xy = laygen.get_inst_pin_xy(inr0.name, 'A', rg_m3m4)
    inr0_b_xy = laygen.get_inst_pin_xy(inr0.name, 'B', rg_m3m4)
    inr0_o_xy = laygen.get_inst_pin_xy(inr0.name, 'O', rg_m3m4)
    izp0_i_xy = laygen.get_inst_pin_xy(izp0.name, 'I', rg_m3m4)
    izp0_o_xy = laygen.get_inst_pin_xy(izp0.name, 'O', rg_m3m4)
    izm0_i_xy = laygen.get_inst_pin_xy(izm0.name, 'I', rg_m3m4)
    izm0_o_xy = laygen.get_inst_pin_xy(izm0.name, 'O', rg_m3m4)
    idff0_i_xy = laygen.get_inst_pin_xy(idff0.name, 'I', rg_m3m4)
    idff0_clk_xy = laygen.get_inst_pin_xy(idff0.name, 'CLK', rg_m3m4)
    idff0_o_xy = laygen.get_inst_pin_xy(idff0.name, 'O', rg_m3m4)

    #reference route coordinate
    y0 = ioai0_a_xy[0][1]
    x0 = laygen.get_xy(obj =ioai0, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_xy(obj =izm0, gridname=rg_m3m4)[0]\
         + laygen.get_xy(obj =izm0.template, gridname=rg_m3m4)[0] * 2 - 1
    x2 = laygen.get_xy(obj =idff0, gridname=rg_m3m4)[0]\
         +laygen.get_xy(obj =idff0.template, gridname=rg_m3m4)[0] - 1
    #saop/saom
    rsaopv0, rsaop0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai0_c_xy[0], np.array([x0, y0 + 3]), rg_m3m4)
    rsaomv0, rsaom0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_c_xy[0], np.array([x0, y0 + 4]), rg_m3m4)
    #rst/sb
    rrstv0, rrst0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai0_b_xy[0], np.array([x0, y0 - 2 + 8]), rg_m3m4)
    rv0, rsb0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai0_d_xy[0], np.array([x0, y0 - 1+6 - 6]), rg_m3m4)
    rrstv1, rrst1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_b_xy[0], np.array([x0, y0 - 2 + 8]), rg_m3m4)
    [rv0, rsb1, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_d_xy[0], ioai0_d_xy[0], y0 - 1, rg_m3m4)
    [rv0, rsb2, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_d_xy[0], idff0_clk_xy[0], y0 - 1, rg_m3m4)
    #ldpo
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai0_o_xy[0], ildpo0_i_xy[0], y0 + 0 - 2 +3, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ildpo0_o_xy[0], ioai0_a_xy[0], y0 - 4, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ildpo0_o_xy[0], izp0_i_xy[0], y0 - 4, rg_m3m4)
    #ldno
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_o_xy[0], ildno0_i_xy[0], y0 + 0, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ildno0_o_xy[0], ioai1_a_xy[0], y0 - 3, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ildno0_o_xy[0], izm0_i_xy[0], y0 - 3, rg_m3m4)
    #nor input
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_o_xy[0], inr0_a_xy[0], y0 + 0, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai0_o_xy[0], inr0_b_xy[0], y0 - 2 +3, rg_m3m4)
    ##nand output(ldndo)
    ##nand input
    #[rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ildpo0_o_xy[0], ind0_b_xy[0], y0 - 4, rg_m3m4)
    #[rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ildno0_o_xy[0], ind0_a_xy[0], y0 - 3, rg_m3m4)
    ##nand output(ldndo)
    #[rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ind0_o_xy[0], izmid0_i_xy[0], y0 + 5, rg_m3m4)
    #final output
    rv0, rzm0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], izp0_o_xy[0], np.array([x1, y0 + 1]), rg_m3m4) #ZP/ZM swapped
    rv0, rzp0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], izm0_o_xy[0], np.array([x1, y0 - 0]), rg_m3m4)
    rv0, rzp1, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], izm0_o_xy[0], idff0_i_xy[0], y0 + 1 - 1, rg_m3m4)
    rv0, rreto0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], idff0_o_xy[0], np.array([x2, y0 - 4]), rg_m3m4)
    #rv0, rzmid0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], izmid0_o_xy[0], np.array([x1, y0 + 2]), rg_m3m4)
    rv0, rzmid0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], inr0_o_xy[0], np.array([x1, y0 + 2]), rg_m3m4)
   
    #pins 
    laygen.boundary_pin_from_rect(rsaop0, rg_m3m4, "SAOP", laygen.layers['pin'][4], size=6, direction='left')
    laygen.pin(name = 'SAOP2', layer = laygen.layers['pin'][3], refobj = rsaopv0, gridname=rg_m3m4, netname='SAOP')
    laygen.boundary_pin_from_rect(rsaom0, rg_m3m4, "SAOM", laygen.layers['pin'][4], size=6, direction='left')
    laygen.pin(name = 'SAOM2', layer = laygen.layers['pin'][3], refobj = rsaomv0, gridname=rg_m3m4, netname='SAOM')
    laygen.boundary_pin_from_rect(rsb0, rg_m3m4, "SB", laygen.layers['pin'][4], size=6, direction='left')
    laygen.boundary_pin_from_rect(rrst0, rg_m3m4, "RST", laygen.layers['pin'][4], size=6, direction='left')
    laygen.pin(name = 'RST2', layer = laygen.layers['pin'][3], refobj = rrstv1, gridname=rg_m3m4, netname='RST')
    laygen.boundary_pin_from_rect(rzp0, rg_m3m4, "ZP", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rzm0, rg_m3m4, "ZM", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rzmid0, rg_m3m4, "ZMID", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rreto0, rg_m3m4, "RETO", laygen.layers['pin'][4], size=6, direction='right')

    # power pin
    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=ioai0, inst_right=idff0)

def generate_sarlogic_wret_v2(laygen, objectname_pfix, templib_logic, placement_grid, routing_grid_m3m4, m=1, origin=np.array([0, 0])):
    """generate sar logic """
    pg = placement_grid
    rg_m3m4 = routing_grid_m3m4

    inv_name = 'inv_1x'
    #oai22_name = 'oai22_1x'
    oai22_name = 'oai22_skewed_1x'
    mux2to1_name = 'mux2to1_1x'
    nand_name = 'nand_1x'
    nor_name = 'nor_' + str(m) + 'x'
    inv_obuf_name = 'inv_' + str(m) + 'x'
    latch_name = 'latch_2ck_1x'
    inv_ret_name = 'inv_1x'
    #dff_name = 'dff_1x'
    space_name = 'space_4x'

    # placement
    ioai0 = laygen.place(name = "I" + objectname_pfix + 'OAI0', templatename = oai22_name,
                            gridname = pg, xy=origin, template_libname=templib_logic)
    ildpo0 = laygen.relplace(name="I" + objectname_pfix + 'INV2', templatename=inv_name,
                            gridname=pg, refinstname=ioai0.name, template_libname=templib_logic)
    ioai1 = laygen.relplace(name = "I" + objectname_pfix + 'OAI1', templatename = oai22_name,
                            gridname = pg, refinstname = ildpo0.name, template_libname=templib_logic)
    ildno0 = laygen.relplace(name="I" + objectname_pfix + 'INV3', templatename=inv_name,
                            gridname=pg, refinstname=ioai1.name, template_libname=templib_logic)
    inr0 = laygen.relplace(name="I" + objectname_pfix + 'NR0', templatename=nor_name,
                           gridname=pg, refinstname=ildno0.name, template_libname=templib_logic)
    izp0 = laygen.relplace(name="I" + objectname_pfix + 'OBUF0', templatename=inv_obuf_name,
                            gridname=pg, refinstname=inr0.name, template_libname=templib_logic)
    izm0 = laygen.relplace(name="I" + objectname_pfix + 'OBUF1', templatename=inv_obuf_name,
                            gridname=pg, refinstname=izp0.name, template_libname=templib_logic)
    isp0 = laygen.relplace(name="I" + objectname_pfix + 'SP0', templatename=space_name,
                            gridname=pg, refinstname=izm0.name, template_libname=templib_logic)
    #idff0 = laygen.relplace(name="I" + objectname_pfix + 'DFF0', templatename=dff_name,
    #                        gridname=pg, refinstname=isp0.name, template_libname=templib_logic)
    iinv0 = laygen.relplace(name="I" + objectname_pfix + 'INV0', templatename=inv_ret_name,
                            gridname=pg, refinstname=isp0.name, template_libname=templib_logic)
    ilatch0 = laygen.relplace(name="I" + objectname_pfix + 'DFF0', templatename=latch_name,
                            gridname=pg, refinstname=iinv0.name, template_libname=templib_logic)

    # internal pins
    ioai0_a_xy = laygen.get_inst_pin_xy(ioai0.name, 'A', rg_m3m4)
    ioai0_b_xy = laygen.get_inst_pin_xy(ioai0.name, 'B', rg_m3m4)
    ioai0_c_xy = laygen.get_inst_pin_xy(ioai0.name, 'C', rg_m3m4)
    ioai0_d_xy = laygen.get_inst_pin_xy(ioai0.name, 'D', rg_m3m4)
    ioai0_o_xy = laygen.get_inst_pin_xy(ioai0.name, 'O', rg_m3m4)
    ildpo0_i_xy = laygen.get_inst_pin_xy(ildpo0.name, 'I', rg_m3m4)
    ildpo0_o_xy = laygen.get_inst_pin_xy(ildpo0.name, 'O', rg_m3m4)
    ioai1_a_xy = laygen.get_inst_pin_xy(ioai1.name, 'A', rg_m3m4)
    ioai1_b_xy = laygen.get_inst_pin_xy(ioai1.name, 'B', rg_m3m4)
    ioai1_c_xy = laygen.get_inst_pin_xy(ioai1.name, 'C', rg_m3m4)
    ioai1_d_xy = laygen.get_inst_pin_xy(ioai1.name, 'D', rg_m3m4)
    ioai1_o_xy = laygen.get_inst_pin_xy(ioai1.name, 'O', rg_m3m4)
    ildno0_i_xy = laygen.get_inst_pin_xy(ildno0.name, 'I', rg_m3m4)
    ildno0_o_xy = laygen.get_inst_pin_xy(ildno0.name, 'O', rg_m3m4)
    inr0_a_xy = laygen.get_inst_pin_xy(inr0.name, 'A', rg_m3m4)
    inr0_b_xy = laygen.get_inst_pin_xy(inr0.name, 'B', rg_m3m4)
    inr0_o_xy = laygen.get_inst_pin_xy(inr0.name, 'O', rg_m3m4)
    izp0_i_xy = laygen.get_inst_pin_xy(izp0.name, 'I', rg_m3m4)
    izp0_o_xy = laygen.get_inst_pin_xy(izp0.name, 'O', rg_m3m4)
    izm0_i_xy = laygen.get_inst_pin_xy(izm0.name, 'I', rg_m3m4)
    izm0_o_xy = laygen.get_inst_pin_xy(izm0.name, 'O', rg_m3m4)
    iinv0_i_xy = laygen.get_inst_pin_xy(iinv0.name, 'I', rg_m3m4)
    iinv0_o_xy = laygen.get_inst_pin_xy(iinv0.name, 'O', rg_m3m4)
    ilatch0_i_xy = laygen.get_inst_pin_xy(ilatch0.name, 'I', rg_m3m4)
    ilatch0_clk_xy = laygen.get_inst_pin_xy(ilatch0.name, 'CLK', rg_m3m4)
    ilatch0_clkb_xy = laygen.get_inst_pin_xy(ilatch0.name, 'CLKB', rg_m3m4)
    ilatch0_o_xy = laygen.get_inst_pin_xy(ilatch0.name, 'O', rg_m3m4)

    #reference route coordinate
    y0 = ioai0_a_xy[0][1]
    x0 = laygen.get_xy(obj =ioai0, gridname=rg_m3m4)[0] + 1
    x1 = laygen.get_xy(obj =izm0, gridname=rg_m3m4)[0]\
         + laygen.get_xy(obj =izm0.template, gridname=rg_m3m4)[0] * 2 - 1
    #x2 = laygen.get_xy(obj =idff0, gridname=rg_m3m4)[0]\
    #     +laygen.get_xy(obj =idff0.template, gridname=rg_m3m4)[0] - 1
    x2 = laygen.get_xy(obj =ilatch0, gridname=rg_m3m4)[0]\
         +laygen.get_xy(obj =ilatch0.template, gridname=rg_m3m4)[0] - 1
    #saop/saom
    rsaopv0, rsaop0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai0_c_xy[0], np.array([x0, y0 + 3]), rg_m3m4)
    rsaomv0, rsaom0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_c_xy[0], np.array([x0, y0 + 4]), rg_m3m4)
    #rst/sb
    rrstv0, rrst0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai0_b_xy[0], np.array([x0, y0 - 2 + 8]), rg_m3m4)
    rv0, rsb0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai0_d_xy[0], np.array([x0, y0 - 3]), rg_m3m4)
    rrstv1, rrst1 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_b_xy[0], np.array([x0, y0 - 2 + 8]), rg_m3m4)
    [rv0, rsb1, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_d_xy[0], ioai0_d_xy[0], y0 - 3, rg_m3m4)
    #[rv0, rsb2, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_d_xy[0], idff0_clk_xy[0], y0 - 1, rg_m3m4)
    [rv0, rsb2, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_d_xy[0], iinv0_i_xy[0], y0 - 3, rg_m3m4)
    [rv0, rsb3, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], iinv0_i_xy[0], ilatch0_clkb_xy[0], y0 - 3, rg_m3m4)
    [rv0, rs1, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], iinv0_o_xy[0], ilatch0_clk_xy[0], y0 - 2, rg_m3m4)
    #ldpo
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai0_o_xy[0], ildpo0_i_xy[0], y0 + 1, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ildpo0_o_xy[0], ioai0_a_xy[0], y0 - 4 + 3, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ildpo0_o_xy[0], izp0_i_xy[0], y0 - 4 + 3, rg_m3m4)
    #ldno
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_o_xy[0], ildno0_i_xy[0], y0 + 0, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ildno0_o_xy[0], ioai1_a_xy[0], y0 - 2, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ildno0_o_xy[0], izm0_i_xy[0], y0 - 2, rg_m3m4)
    #nor input
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai1_o_xy[0], inr0_a_xy[0], y0 + 0, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], ioai0_o_xy[0], inr0_b_xy[0], y0 - 2 +3, rg_m3m4)
    #final output
    rv0, rzm0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], izp0_o_xy[0], np.array([x1, y0 + 1]), rg_m3m4) #ZP/ZM swapped
    rv0, rzp0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], izm0_o_xy[0], np.array([x1, y0 - 0]), rg_m3m4)
    #rv0, rzp1, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], izm0_o_xy[0], idff0_i_xy[0], y0 + 1 - 1, rg_m3m4)
    #rv0, rreto0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], idff0_o_xy[0], np.array([x2, y0 - 4]), rg_m3m4)
    rv0, rzp1, rv1 = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4], izm0_o_xy[0], ilatch0_i_xy[0], y0 + 1 - 1, rg_m3m4)
    #rv0, rreto0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ilatch0_o_xy[0], np.array([x2, y0 - 4]), rg_m3m4)
    rv0, rreto0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], ilatch0_o_xy[0], np.array([x2, y0 + 2]), rg_m3m4)
    rv0, rzmid0 = laygen.route_vh(laygen.layers['metal'][3], laygen.layers['metal'][4], inr0_o_xy[0], np.array([x1, y0 + 2]), rg_m3m4)
   
    #pins 
    laygen.boundary_pin_from_rect(rsaop0, rg_m3m4, "SAOP", laygen.layers['pin'][4], size=6, direction='left')
    laygen.pin(name = 'SAOP2', layer = laygen.layers['pin'][3], refobj = rsaopv0, gridname=rg_m3m4, netname='SAOP')
    laygen.boundary_pin_from_rect(rsaom0, rg_m3m4, "SAOM", laygen.layers['pin'][4], size=6, direction='left')
    laygen.pin(name = 'SAOM2', layer = laygen.layers['pin'][3], refobj = rsaomv0, gridname=rg_m3m4, netname='SAOM')
    laygen.boundary_pin_from_rect(rsb0, rg_m3m4, "SB", laygen.layers['pin'][4], size=6, direction='left')
    laygen.boundary_pin_from_rect(rrst0, rg_m3m4, "RST", laygen.layers['pin'][4], size=6, direction='left')
    laygen.pin(name = 'RST2', layer = laygen.layers['pin'][3], refobj = rrstv1, gridname=rg_m3m4, netname='RST')
    laygen.boundary_pin_from_rect(rzp0, rg_m3m4, "ZP", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rzm0, rg_m3m4, "ZM", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rzmid0, rg_m3m4, "ZMID", laygen.layers['pin'][4], size=6, direction='right')
    laygen.boundary_pin_from_rect(rreto0, rg_m3m4, "RETO", laygen.layers['pin'][4], size=6, direction='right')

    # power pin
    #create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=ioai0, inst_right=idff0)
    create_power_pin_from_inst(laygen, layer=laygen.layers['pin'][2], gridname=rg_m1m2, inst_left=ioai0, inst_right=ilatch0)

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
    rg_m2m3_thick = 'route_M2_M3_thick'
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
    #sarlogic generation
    m=2
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        m=sizedict['sarlogic']['m']
   
    cellname='sarlogic_wret_v2'
    print(cellname+" generating")
    mycell_list.append(cellname)
    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)
    generate_sarlogic_wret_v2(laygen, objectname_pfix='SL0', templib_logic=logictemplib,
                    placement_grid=pg, routing_grid_m3m4=rg_m3m4, m=m, origin=np.array([0, 0]))
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
