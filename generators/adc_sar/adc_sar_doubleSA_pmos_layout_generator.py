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

def generate_doubleSA_pmos(laygen, objectname_pfix, workinglib, placement_grid,
                          routing_grid_m1m2, routing_grid_m1m2_thick, routing_grid_m2m3,
                          routing_grid_m2m3_thick, routing_grid_m3m4, routing_grid_m4m5,
                          origin=np.array([0, 0])):
    """generate double tail strongarm latch"""
    sa_1st_name = 'doubleSA_pmos_1st'
    sa_2nd_name = 'doubleSA_pmos_2nd'
    #grids
    pg = placement_grid
    rg_m1m2 = routing_grid_m1m2
    rg_m1m2_thick = routing_grid_m1m2_thick
    rg_m2m3 = routing_grid_m2m3
    rg_m2m3_thick = routing_grid_m2m3_thick
    rg_m3m4 = routing_grid_m3m4
    rg_m4m5 = routing_grid_m4m5

    #placement
    i1st=laygen.relplace(name="I" + objectname_pfix + '1st', templatename=sa_1st_name,
                         gridname=pg, refinstname=None, direction='right', template_libname=workinglib)
    i2nd=laygen.relplace(name="I" + objectname_pfix + '2nd', templatename=sa_2nd_name,
                         gridname=pg, refinstname=i1st.name, direction='top', transform='R0', template_libname=workinglib)

    #route
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                laygen.get_inst_pin_xy(i1st.name, 'OP', rg_m3m4)[0],
                                laygen.get_inst_pin_xy(i2nd.name, 'OP', rg_m4m5)[0],
                                laygen.get_inst_xy(i2nd.name, rg_m3m4)[1]-2, rg_m3m4,
                                layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                laygen.get_inst_pin_xy(i1st.name, 'OM', rg_m3m4)[1],
                                laygen.get_inst_pin_xy(i2nd.name, 'OM', rg_m4m5)[0],
                                laygen.get_inst_xy(i2nd.name, rg_m3m4)[1]-2, rg_m3m4,
                                layerv1=laygen.layers['metal'][5], gridname1=rg_m4m5)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                laygen.get_inst_pin_xy(i1st.name, 'INTP', rg_m3m4)[0],
                                laygen.get_inst_pin_xy(i2nd.name, 'INTP', rg_m3m4)[0],
                                laygen.get_inst_xy(i2nd.name, rg_m3m4)[1]+2, rg_m3m4)
    [rv0, rh0, rv1] = laygen.route_vhv(laygen.layers['metal'][3], laygen.layers['metal'][4],
                                laygen.get_inst_pin_xy(i1st.name, 'INTM', rg_m3m4)[0],
                                laygen.get_inst_pin_xy(i2nd.name, 'INTM', rg_m3m4)[0],
                                laygen.get_inst_xy(i2nd.name, rg_m3m4)[1]+2, rg_m3m4)

    #pin
    laygen.pin(name='INP', layer=laygen.layers['pin'][3], xy=laygen.get_inst_pin_xy(i1st.name, 'INP', rg_m3m4), gridname=rg_m3m4)
    laygen.pin(name='INM', layer=laygen.layers['pin'][3], xy=laygen.get_inst_pin_xy(i1st.name, 'INM', rg_m3m4), gridname=rg_m3m4)
    laygen.pin(name='OSP', layer=laygen.layers['pin'][3], xy=laygen.get_inst_pin_xy(i1st.name, 'OSP', rg_m3m4), gridname=rg_m3m4)
    laygen.pin(name='OSM', layer=laygen.layers['pin'][3], xy=laygen.get_inst_pin_xy(i1st.name, 'OSM', rg_m3m4), gridname=rg_m3m4)
    laygen.pin(name='CLKB', layer=laygen.layers['pin'][5], xy=laygen.get_inst_pin_xy(i1st.name, 'CLKB', rg_m4m5), gridname=rg_m4m5)
    laygen.pin(name='INTP', layer=laygen.layers['pin'][3], xy=laygen.get_inst_pin_xy(i2nd.name, 'INTP', rg_m3m4), gridname=rg_m3m4)
    laygen.pin(name='INTM', layer=laygen.layers['pin'][3], xy=laygen.get_inst_pin_xy(i2nd.name, 'INTM', rg_m3m4), gridname=rg_m3m4)
    laygen.pin(name='OUTP', layer=laygen.layers['pin'][5], xy=laygen.get_inst_pin_xy(i2nd.name, 'OUTP', rg_m4m5), gridname=rg_m4m5)
    laygen.pin(name='OUTM', layer=laygen.layers['pin'][5], xy=laygen.get_inst_pin_xy(i2nd.name, 'OUTM', rg_m4m5), gridname=rg_m4m5)

    # vdd/vss
    # m3
    pdict_m3m4 = laygen.get_inst_pin_xy(None, None, rg_m3m4)
    rvddl_m3=[]
    rvssl_m3=[]
    rvddr_m3=[]
    rvssr_m3=[]
    xsa_center = int(laygen.get_template_size(name=sa_1st_name, gridname=rg_m3m4, libname=workinglib)[0] / 2)
    vddl=0
    vddr=0
    vssl=0
    vssr=0
    for p in pdict_m3m4[i2nd.name]:
        if p.startswith('VDDL'):
            r0=laygen.route(None, laygen.layers['metal'][3], xy0=pdict_m3m4[i2nd.name][p][1], 
                            xy1=np.array([pdict_m3m4[i2nd.name][p][0][0],pdict_m3m4[i1st.name][p][0][1]]), gridname0=rg_m3m4)
            rvddl_m3.append(r0)
            laygen.pin(name='VDDL'+str(vddl), layer=laygen.layers['pin'][3],
               xy=laygen.get_rect_xy(r0.name, rg_m3m4), gridname=rg_m3m4, netname='VDD')
            vddl+=1
        if p.startswith('VDDR'):
            r0=laygen.route(None, laygen.layers['metal'][3], xy0=pdict_m3m4[i2nd.name][p][1],
                            xy1=np.array([pdict_m3m4[i2nd.name][p][0][0],pdict_m3m4[i1st.name][p][0][1]]), gridname0=rg_m3m4)
            rvddr_m3.append(r0)
            laygen.pin(name='VDDR'+str(vddr), layer=laygen.layers['pin'][3],
               xy=laygen.get_rect_xy(r0.name, rg_m3m4), gridname=rg_m3m4, netname='VDD')
            vddr+=1
        if p.startswith('VSSL'):
            r0=laygen.route(None, laygen.layers['metal'][3], xy0=pdict_m3m4[i2nd.name][p][1], 
                            xy1=np.array([pdict_m3m4[i2nd.name][p][0][0],pdict_m3m4[i1st.name][p][0][1]]), gridname0=rg_m3m4)
            rvddl_m3.append(r0)
            laygen.pin(name='VSSL'+str(vssl), layer=laygen.layers['pin'][3],
                   xy=laygen.get_rect_xy(r0.name, rg_m3m4), gridname=rg_m3m4, netname='VSS')
            vssl+=1
        if p.startswith('VSSR'):
            r0=laygen.route(None, laygen.layers['metal'][3], xy0=pdict_m3m4[i2nd.name][p][1], 
                            xy1=np.array([pdict_m3m4[i2nd.name][p][0][0],pdict_m3m4[i1st.name][p][0][1]]), gridname0=rg_m3m4)
            rvddr_m3.append(r0)
            laygen.pin(name='VSSR'+str(vssr), layer=laygen.layers['pin'][3],
                   xy=laygen.get_rect_xy(r0.name, rg_m3m4), gridname=rg_m3m4, netname='VSS')
            vssr+=1

    '''
    for p in pdict_m3m4[iret.name]:
        if p.startswith('VSS'):
            r0=laygen.route(None, laygen.layers['metal'][3], xy0=pdict_m3m4[iret.name][p][0], xy1=pdict_m3m4[isp[-1].name][p][0],
                            gridname0=rg_m3m4)
            if pdict_m3m4[iret.name][p][0][0] < xret_center:
                rvssl_m3.append(r0)
            else:
                rvssr_m3.append(r0)
    '''
    '''
    #offset pair
    [iofsttapbl0, iofsttap0, iofsttapbr0, iofstckbl0, iofstck0, iofstckbr0,
     iofstinbl0, iofstindmyl0, iofstinl0, iofstinr0, iofstindmyr0, iofstinbr0]=\
    [None, None, None, None, None, None,
     None, None, None, None, None, None]
    #generate_clkdiffpair(laygen, objectname_pfix=objectname_pfix+'OFST0', placement_grid=pg,
    #                     routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick, routing_grid_m2m3=rg_m2m3,
    #                     devname_mos_boundary=devname_pmos_boundary, devname_mos_body=devname_pmos_body, devname_mos_dmy=devname_pmos_dmy,
    #                     devname_tap_boundary=devname_ntap_boundary, devname_tap_body=devname_ntap_body,
    #                     m_in=m_in, m_in_dmy=m_in_dmy, m_clkh=m_clkh, m_clkh_dmy=m_clkh_dmy, m_tap=m_tap, origin=origin)

    #main pair
    #mainpair_origin = laygen.get_inst_xy(iofstinbl0.name, pg) + laygen.get_template_size(iofstinbl0.cellname, pg) * np.array([0, 1])
    mainpair_origin = origin
    [imaintapbl0, imaintap0, imaintapbr0, imainckbl0, imainck0, imainckbr0,
     imaininbl0, imainindmyl0, iofstinl0, imaininl0, imaininr0, iofstinr0, imainindmyr0, imaininbr0]=\
    generate_clkdiffpair_ofst(laygen, objectname_pfix=objectname_pfix+'MAIN0', placement_grid=pg,
                         routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick, routing_grid_m2m3=rg_m2m3,
                         devname_mos_boundary=devname_pmos_boundary, devname_mos_body=devname_pmos_body, devname_mos_dmy=devname_pmos_dmy,
                         devname_tap_boundary=devname_ntap_boundary, devname_tap_body=devname_ntap_body,
                         m_in=m_in, m_ofst=m_ofst, m_in_dmy=m_in_dmy-m_ofst, m_clkh=m_clkh, m_clkh_dmy=m_clkh_dmy, m_tap=m_tap, origin=mainpair_origin)
    #regen
    regen_origin = laygen.get_inst_xy(imaininbl0.name, pg) + laygen.get_template_size(imaininbl0.cellname, pg) * np.array([0, 1])

    [irgntapbln0, irgntapn0, irgntapbrn0,
     irgnbln0, irgnbufln0, irgndmyln0, irgnln0, irgnln1, irgnrn1, irgnrn0, irgndmyrn0, irgnbufrn0, irgnbrn0,
     irgnblp0, irgnbuflp0, irgndmylp0, irgnlp0, irgnrstlp0, irgnrstlp1, irgnrstrp1, irgnrstrp0, irgnrp0, irgndmyrp0, irgnbufrp0, irgnbrp0,
     irgntapbl0, irgntap0, irgntapbr0]=\
    generate_salatch_regen(laygen, objectname_pfix=objectname_pfix+'RGN0', placement_grid=pg,
                           routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick, routing_grid_m2m3=rg_m2m3, routing_grid_m3m4=rg_m3m4,
                           devname_nmos_boundary=devname_pmos_boundary, devname_nmos_body=devname_pmos_body, devname_nmos_dmy=devname_pmos_dmy,
                           devname_pmos_boundary=devname_nmos_boundary, devname_pmos_body=devname_nmos_body, devname_pmos_dmy=devname_nmos_dmy,
                           devname_ptap_boundary=devname_ntap_boundary, devname_ptap_body=devname_ntap_body,
                           devname_ntap_boundary=devname_ptap_boundary, devname_ntap_body=devname_ptap_body,
                           m_rgnp=m_rgnn, m_rgnp_dmy=m_rgnn_dmy, m_rstp=m_rstn, m_tap=m_tap, m_buf=m_buf, origin=regen_origin)

    #doubleSA input
    din_origin=laygen.get_inst_xy(irgnblp0.name, pg)+laygen.get_template_size(irgnblp0.cellname, pg)*np.array([0,1])
    [idinbl0, idindmyl0, idofstl0, idinl0, idinr0, idofstr0, idindmyr0, idinbr0] = \
    generate_diff_mos_ofst(laygen, objectname_pfix+'DIN0', placement_grid=pg, routing_grid_m1m2=rg_m1m2,
                          devname_mos_boundary=devname_nmos_boundary, devname_mos_body=devname_nmos_body,
                          devname_mos_dmy=devname_nmos_dmy, m=m_in, m_ofst=0, m_dmy=m_in_dmy, origin=din_origin)
    #irgnbuflp1
    #regen-diff pair connections
    for i in range(m_rstn):
        rintm=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                           refinstname0=irgnln1.name, refpinname0='S0', refinstindex0=np.array([-i, 0]), via0=[[0, 0]],
                           refinstname1=irgnrstlp1.name, refpinname1='S0', refinstindex1=np.array([m_rstn-1-i, 0]), via1=[[0, 0]])
        rintp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([0, 0]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                           refinstname0=irgnrn1.name, refpinname0='S0', refinstindex0=np.array([-i, 0]), via0=[[0, 0]],
                           refinstname1=irgnrstrp1.name, refpinname1='S0', refinstindex1=np.array([m_rstn-1-i, 0]), via1=[[0, 0]])
    for i in range(min(m_in, m_rgnn+m_rstn)):
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2, 1]), xy1=np.array([-2, 0]), gridname0=rg_m2m3,
                     refinstname0=imaininl0.name, refpinname0='S0', refinstindex0=np.array([m_in - 1 - i + 1, 0]), via0=[[0, 0]],
                     refinstname1=irgnln1.name, refpinname1='S0', refinstindex1=np.array([-i + 1, 0]), via1=[[0, 0]])
        laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2, 1]), xy1=np.array([-2, 0]), gridname0=rg_m2m3,
                     refinstname0=imaininr0.name, refpinname0='S0', refinstindex0=np.array([m_in - 1 - i + 1, 0]), via0=[[0, 0]],
                     refinstname1=irgnrn1.name, refpinname1='S0', refinstindex1=np.array([-i + 1, 0]), via1=[[0, 0]])
    laygen.boundary_pin_from_rect(rintp, gridname=rg_m2m3, name='INTP', layer=laygen.layers['pin'][3], size=2, direction='top')
    laygen.boundary_pin_from_rect(rintm, gridname=rg_m2m3, name='INTM', layer=laygen.layers['pin'][3], size=2, direction='top')
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refobj0=irgnrstlp1, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refobj1=irgnrstlp1, refpinname1='D0', refinstindex1=np.array([m_rstn-1, 0]))
    laygen.route(None, laygen.layers['metal'][2], xy0=np.array([0, 1]), xy1=np.array([0, 1]), gridname0=rg_m2m3,
                 refobj0=irgnrstrp1, refpinname0='D0', refinstindex0=np.array([0, 0]),
                 refobj1=irgnrstrp1, refpinname1='D0', refinstindex1=np.array([m_rstn-1, 0]))
    
    laygen.via(None, np.array([0, 1]), refinstname=imaininl0.name, refpinname='S0', refinstindex=np.array([m_in-1, 0]), gridname=rg_m2m3)
    laygen.via(None, np.array([0, 1]), refinstname=imaininr0.name, refpinname='S0', refinstindex=np.array([m_in-1, 0]), gridname=rg_m2m3)
    for i in range(m_rstn):
        laygen.via(None, np.array([0, 1]), refinstname=irgnrstlp1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
        laygen.via(None, np.array([0, 1]), refinstname=irgnrstrp1.name, refpinname='D0', refinstindex=np.array([i, 0]), gridname=rg_m1m2)
    #clk connection
    xy0=laygen.get_inst_pin_xy(imainck0.name, pinname='G0', gridname=rg_m2m3, index=np.array([m_clkh - 1, 0]), sort=True)[0]
    y0=laygen.get_inst_xy(imaintap0.name, rg_m3m4)[1]-1
    xy1=laygen.get_inst_pin_xy(irgnrstlp1.name, pinname='G0', gridname=rg_m2m3, index=np.array([m_clkh - 1, 0]), sort=True)[0]
    rclk=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0]+1, y0]), xy1=np.array([1, 0-4-1]), gridname0=rg_m2m3,
                      refinstname1=irgnrstlp1.name, refpinname1='G0', refinstindex1=np.array([m_rstn-1, 0])
                      )
    xy0=laygen.get_rect_xy(rclk.name, rg_m3m4, sort=True)
    #laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([-2*m_rstn, 0]), xy1=xy0[1]+np.array([0, 0]), gridname0=rg_m3m4, via1=[[0, 0]])
    #rclk2 = laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([0, 0]), xy1=xy0[1]+np.array([2*m_rstn, 0]), gridname0=rg_m3m4)
    laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([-1*l_clkb_m4, 0]), xy1=xy0[1]+np.array([0, 0]), gridname0=rg_m3m4, via1=[[0, 0]])
    rclk2 = laygen.route(None, laygen.layers['metal'][4], xy0=xy0[1]+np.array([0, 0]), xy1=xy0[1]+np.array([l_clkb_m4, 0]), gridname0=rg_m3m4)
    xy0=laygen.get_rect_xy(rclk2.name, rg_m4m5, sort=True)
    rclk3 = laygen.route(None, laygen.layers['metal'][5], xy0=xy0[0]+np.array([l_clkb_m4, 0]), xy1=xy0[0]+np.array([l_clkb_m4, 5]), gridname0=rg_m4m5, via0=[[0, 0]])
    laygen.boundary_pin_from_rect(rclk3, gridname=rg_m4m5, name='CLKB', layer=laygen.layers['pin'][5], size=4, direction='top')
    laygen.via(None, np.array([1, 0]), refinstname=imainck0.name, refpinname='G0', refinstindex=np.array([m_clkh-1, 0]), gridname=rg_m2m3)
    laygen.via(None, np.array([1, 0]), refinstname=irgnrstlp1.name, refpinname='G0', refinstindex=np.array([m_rstn-1, 0]), gridname=rg_m2m3)
    #input connection
    y0=laygen.get_inst_xy(imaintap0.name, rg_m3m4)[1]
    y1=laygen.get_inst_xy(irgntap0.name, rg_m2m3)[1]
    xy0=laygen.get_inst_pin_xy(imaininl0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    rinp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0]+1-1, y0]), xy1=np.array([1-1, 0]), gridname0=rg_m2m3,
                      refinstname1=imaininl0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.boundary_pin_from_rect(rinp, gridname=rg_m3m4, name='INP', layer=laygen.layers['pin'][3], size=4, direction='bottom')
    laygen.via(None, np.array([1-1, 0]), refinstname=imaininl0.name, refpinname='G0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    xy0=laygen.get_inst_pin_xy(imaininr0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    rinm=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0]-1+1, y0]), xy1=np.array([1-1, 0]), gridname0=rg_m2m3,
                      refinstname1=imaininr0.name, refpinname1='G0', refinstindex1=np.array([0, 0]))
    laygen.boundary_pin_from_rect(rinm, gridname=rg_m3m4, name='INM', layer=laygen.layers['pin'][3], size=4, direction='bottom')
    laygen.via(None, np.array([1-1, 0]), refinstname=imaininr0.name, refpinname='G0', refinstindex=np.array([0, 0]), gridname=rg_m2m3)
    #output connection (outp)
    x_center=laygen.get_rect_xy(rclk.name, rg_m3m4, sort=True)[0][0]
    y1=laygen.get_inst_xy(irgntap0.name, rg_m3m4)[1]-4
    xy0=laygen.get_inst_pin_xy(irgnbuflp0.name, pinname='D0', gridname=rg_m3m4, index=np.array([m_buf-1, 0]), sort=True)[0]
    routp=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0], y1+4]), xy1=np.array([0, 1]), gridname0=rg_m3m4,
                      refinstname1=irgnbuflp0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]),
                      direction='top')
    routp2=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1]), xy1=np.array([x_center-l_clkb_m4-2, y1]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    routp2b=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1+2]), xy1=np.array([x_center-l_clkb_m4-2, y1+2]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    xy1=laygen.get_rect_xy(routp2.name, rg_m4m5, sort=True)
    routp3 = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[1], xy1=xy1[1]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    routp3b = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[1]+np.array([0, 2]), xy1=xy1[1]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    laygen.boundary_pin_from_rect(routp3, gridname=rg_m4m5, name='OUTP', layer=laygen.layers['pin'][5], size=4, direction='top')
    #output connection (outm)
    y1=laygen.get_inst_xy(irgntap0.name, rg_m3m4)[1]-4
    xy0=laygen.get_inst_pin_xy(irgnbufrp0.name, pinname='D0', gridname=rg_m3m4, index=np.array([m_buf-1, 0]), sort=True)[0]
    routm=laygen.route(None, laygen.layers['metal'][3], xy0=np.array([xy0[0], y1+4]), xy1=np.array([0, 1]), gridname0=rg_m3m4,
                      refinstname1=irgnbufrp0.name, refpinname1='D0', refinstindex1=np.array([m_buf-1, 0]),
                      direction='top')
    routm2=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1]), xy1=np.array([x_center+l_clkb_m4+2, y1]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    routm2b=laygen.route(None, laygen.layers['metal'][4], xy0=np.array([xy0[0], y1+2]), xy1=np.array([x_center+l_clkb_m4+2, y1+2]),
                        gridname0=rg_m3m4, via0=[[0, 0]])
    xy1=laygen.get_rect_xy(routm2.name, rg_m4m5, sort=True)
    routm3 = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[0]+np.array([0, 0]), xy1=xy1[0]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    routm3b = laygen.route(None, laygen.layers['metal'][5], xy0=xy1[0]+np.array([0, 2]), xy1=xy1[0]+np.array([0, 6]), gridname0=rg_m4m5, via0=[[0, 0]])
    laygen.boundary_pin_from_rect(routm3, gridname=rg_m4m5, name='OUTM', layer=laygen.layers['pin'][5], size=4, direction='top')
    #offset input connection
    y1=laygen.get_inst_xy(irgntap0.name, rg_m2m3)[1]
    xy0=laygen.get_inst_pin_xy(iofstinl0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    xy1=laygen.get_rect_xy(routp.name, rg_m2m3, sort=True)[0]
    rosp=laygen.route(None, laygen.layers['metal'][3], xy0=[xy1[0]+3, y1], xy1=[0, 0], gridname0=rg_m2m3, 
                      refobj1=iofstinl0, refpinname1='G0', direction='y', via1=[[0, 0]])
    laygen.boundary_pin_from_rect(rosp, gridname=rg_m3m4, name='OSP', layer=laygen.layers['pin'][3], size=4, direction='top')
    xy0=laygen.get_inst_pin_xy(iofstinr0.name, pinname='G0', gridname=rg_m2m3, index=np.array([0, 0]), sort=True)[0]
    xy1=laygen.get_rect_xy(routm.name, rg_m2m3, sort=True)[0]
    #rosm=laygen.route(None, laygen.layers['metal'][3], xy0=[xy1[0]-3, y1], xy1=[xy1[0]-3, xy0[1]], gridname0=rg_m2m3, via1=[[0, 0]])
    rosm=laygen.route(None, laygen.layers['metal'][3], xy0=[xy1[0]-3, y1], xy1=[0, 0], gridname0=rg_m2m3, 
                      refobj1=iofstinr0, refpinname1='G0', direction='y', via1=[[0, 0]])
    #laygen.route(None, laygen.layers['metal'][2], xy0=[0, 0], xy1=[xy1[0]-3, xy0[1]], gridname0=rg_m2m3,
    #             refinstname0=iofstinr0.name, refpinname0='G0', refinstindex0=np.array([0, 0]))
    laygen.boundary_pin_from_rect(rosm, gridname=rg_m3m4, name='OSM', layer=laygen.layers['pin'][3], size=4, direction='top')

    #VDD/VSS
    #num_vert_pwr = 20
    rvss1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 1]), xy1=np.array([2*num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
                        refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    rvss1b = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, -1]), xy1=np.array([2*num_vert_pwr, -1]), gridname0=rg_m1m2_thick,
                        refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    rvss2 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 1]), xy1=np.array([2*num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
                        refinstname0=irgntapn0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=irgntapn0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    rvss = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 1]), xy1=np.array([2*num_vert_pwr, 1]), gridname0=rg_m1m2_thick,
                        refinstname0=irgntap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    rvssb = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, -1]), xy1=np.array([2*num_vert_pwr, -1]), gridname0=rg_m1m2_thick,
                        refinstname0=irgntap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                        refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
    rvdd0 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, 0]), xy1=np.array([2*num_vert_pwr, 0]), gridname0=rg_m1m2,
                        refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 1]),
                        refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 1])
                       )
    rvdd1 = laygen.route(None, laygen.layers['metal'][2], xy0=np.array([-2*num_vert_pwr, -1]), xy1=np.array([2*num_vert_pwr, -1]), gridname0=rg_m1m2_pin,
                        refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 4]),
                        refinstname1=imaintap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 4])
                       )
    #rvdd_pin_xy = laygen.get_rect_xy(rvdd.name, rg_m1m2_thick)
    rvss1_pin_xy = laygen.get_rect_xy(rvss1.name, rg_m1m2_thick)
    rvss2_pin_xy = laygen.get_rect_xy(rvss2.name, rg_m1m2_thick)
    rvss_pin_xy = laygen.get_rect_xy(rvss.name, rg_m1m2_thick)

    #laygen.pin(name='VDD0', layer=laygen.layers['pin'][2], xy=rvdd_pin_xy, gridname=rg_m1m2_thick, netname='VDD')
    laygen.pin(name='VSS2', layer=laygen.layers['pin'][2], xy=rvss1_pin_xy, gridname=rg_m1m2_thick, netname='VSS')
    laygen.pin(name='VSS1', layer=laygen.layers['pin'][2], xy=rvss2_pin_xy, gridname=rg_m1m2_thick, netname='VSS')
    laygen.pin(name='VSS0', layer=laygen.layers['pin'][2], xy=rvss_pin_xy, gridname=rg_m1m2_thick, netname='VSS')

    #vdd/vss vertical
    i=0
    for i in range(num_vert_pwr):
        rvvss_l = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2*i-1, -1]), xy1=np.array([-2*i-1, -1]), gridname0=rg_m2m3_thick,
                               refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                               refinstname1=irgntap0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0])
                               )
        rvvss_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+1, -1]), xy1=np.array([2*i+1, -1]), gridname0=rg_m2m3_thick,
                               refinstname0=imaintap0.name, refpinname0='TAP1', refinstindex0=np.array([m_tap-1, 0]),
                               refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                               )
        laygen.via(None, np.array([-2*i-1, 1]), refinstname=irgntap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 1]), refinstname=irgntap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-1, -1]), refinstname=irgntap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, -1]), refinstname=irgntap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        laygen.pin(name='VSSL'+str(i), layer=laygen.layers['pin'][3],
                   xy=laygen.get_rect_xy(rvvss_l.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VSS')
        laygen.pin(name='VSSR'+str(i), layer=laygen.layers['pin'][3],
                   xy=laygen.get_rect_xy(rvvss_r.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VSS')

        rvvdd_l = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([-2*i-2, -1]), xy1=np.array([-2*i-2, -1]), gridname0=rg_m2m3_thick,
                               refinstname0=imaintap0.name, refpinname0='TAP0', refinstindex0=np.array([0, 0]),
                               refinstname1=irgntap0.name, refpinname1='TAP0', refinstindex1=np.array([0, 0])
                       )
        rvvdd_r = laygen.route(None, laygen.layers['metal'][3], xy0=np.array([2*i+2, -1]), xy1=np.array([2*i+2, -1]), gridname0=rg_m2m3_thick,
                               refinstname0=imaintap0.name, refpinname0='TAP1', refinstindex0=np.array([m_tap-1, 0]),
                               refinstname1=irgntap0.name, refpinname1='TAP1', refinstindex1=np.array([m_tap-1, 0])
                       )
        laygen.via(None, np.array([-2*i-1, 1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-1, 1]), refinstname=irgntapn0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, 1]), refinstname=irgntapn0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-1, -1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([2*i+1, -1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 0]),
                       gridname=rg_m2m3_thick)
        laygen.via(None, np.array([-2*i-2, 0]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 1]),
                       gridname=rg_m2m3)
        laygen.via(None, np.array([2*i+2, 0]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 1]),
                       gridname=rg_m2m3)
        laygen.via(None, np.array([-2*i-2, -1]), refinstname=imaintap0.name, refpinname='TAP0', refinstindex=np.array([0, 4]),
                       gridname=rg_m2m3_pin)
        laygen.via(None, np.array([2*i+2, -1]), refinstname=imaintap0.name, refpinname='TAP1', refinstindex=np.array([m_tap-1, 4]),
                       gridname=rg_m2m3_pin)

        laygen.pin(name='VDDL'+str(i), layer=laygen.layers['pin'][3],
                   xy=laygen.get_rect_xy(rvvdd_l.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VDD')
        laygen.pin(name='VDDR'+str(i), layer=laygen.layers['pin'][3],
                   xy=laygen.get_rect_xy(rvvdd_r.name, rg_m2m3_thick), gridname=rg_m2m3_thick, netname='VDD')
    '''

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
    rg_m1m2_thick = 'route_M1_M2_basic_thick'
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
    #salatch generation (wboundary)
    #cellname = 'salatch'
    cellname = 'doubleSA_pmos'
    print(cellname+" generating")
    mycell_list.append(cellname)
    m_sa=8
    m_rst_sa=8
    m_rgnn_sa=2
    m_buf_sa=8
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        m_sa=sizedict['salatch']['m']
        m_rst_sa=sizedict['salatch']['m_rst']
        m_rgnn_sa=sizedict['salatch']['m_rgnn']
        m_buf_sa=sizedict['salatch']['m_buf']
        #m_sa=sizedict['salatch_m']
        #m_rst_sa=sizedict['salatch_m_rst']
        #m_rgnn_sa=sizedict['salatch_m_rgnn']
        #m_buf_sa=sizedict['salatch_m_buf']
    m_in=int(m_sa/2)            #4
    m_clkh=m_in #max(1, m_in)                 #4
    m_rstn=int(m_rst_sa/2)                    #1
    m_buf=int(m_buf_sa/2)
    m_rgnn=int(m_rgnn_sa/2) 
    m_ofst=1

    laygen.add_cell(cellname)
    laygen.sel_cell(cellname)

    sa_origin=np.array([0, 0])

    #salatch body
    # 1. generate without spacing
    generate_doubleSA_pmos(laygen, objectname_pfix='SA0', workinglib=workinglib,
                                placement_grid=pg, routing_grid_m1m2=rg_m1m2, routing_grid_m1m2_thick=rg_m1m2_thick,
                                routing_grid_m2m3=rg_m2m3, routing_grid_m2m3_thick=rg_m2m3_thick, routing_grid_m3m4=rg_m3m4, routing_grid_m4m5=rg_m4m5,
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
