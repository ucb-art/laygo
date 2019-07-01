# -*- coding: utf-8 -*-
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

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# noinspection PyUnresolvedReferences,PyCompatibility
from builtins import *

import os
import pkg_resources

from bag.design import Module


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'sar_wsamp.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__sar_wsamp(Module):
    """Module for library adc_sar_templates cell sar_wsamp.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, sar_lch, sar_pw, sar_nw, sar_sa_m, sar_sa_m_d, sar_sa_m_rst, sar_sa_m_rst_d, sar_sa_m_rgnn, sar_sa_m_rgnp_d,
               sar_sa_m_buf, doubleSA, sar_sa_m_smallrgnp,
               vref_sf_m_mirror, vref_sf_m_bias, vref_sf_m_off, vref_sf_m_in, vref_sf_m_bias_dum, vref_sf_m_in_dum,
               vref_sf_m_byp, vref_sf_m_byp_bias, vref_sf_bias_current, vref_sf,
               sar_drv_m_list, sar_ckgen_m, sar_ckgen_fo, sar_ckgen_ndelay, sar_ckgen_fast, sar_ckgen_muxfast,
               sar_logic_m, sar_fsm_m, sar_ret_m, sar_ret_fo, sar_num_inv_bb, sar_device_intent, sar_c_m, sar_rdx_array,
               samp_lch, samp_wp, samp_wn, samp_fgn, samp_fg_inbuf_list, samp_fg_outbuf_list, samp_nduml, samp_ndumr, samp_nsep, samp_intent,
               samp_tgate, num_bits, samp_use_laygo,
               sf_lch, sf_nw, sf_m_mirror, sf_m_bias, sf_m_off, sf_m_in, sf_m_bias_dum, sf_m_in_dum, sf_m_byp, sf_m_byp_bias,
               sf_intent, bias_current, use_sf):
        """To be overridden by subclasses to design this module.

        This method should fill in values for all parameters in
        self.parameters.  To design instances of this module, you can
        call their design() method or any other ways you coded.

        To modify schematic structure, call:

        rename_pin()
        delete_instance()
        replace_instance_master()
        reconnect_instance_terminal()
        restore_instance()
        array_instance()
        """
        self.parameters['sar_lch'] = sar_lch
        self.parameters['sar_pw'] = sar_pw
        self.parameters['sar_nw'] = sar_nw
        self.parameters['sar_sa_m'] = sar_sa_m
        self.parameters['sar_sa_m_d'] = sar_sa_m_d
        self.parameters['sar_sa_m_rst'] = sar_sa_m_rst
        self.parameters['sar_sa_m_rst_d'] = sar_sa_m_rst
        self.parameters['sar_sa_m_rgnn'] = sar_sa_m_rgnn
        self.parameters['sar_sa_m_rgnp_d'] = sar_sa_m_rgnp_d
        self.parameters['sar_sa_m_buf'] = sar_sa_m_buf
        self.parameters['sar_sa_m_smallrgnp'] = sar_sa_m_smallrgnp
        self.parameters['doubleSA'] = doubleSA
        self.parameters['vref_sf_m_mirror'] = vref_sf_m_mirror
        self.parameters['vref_sf_m_bias'] = vref_sf_m_bias
        self.parameters['vref_sf_m_in'] = vref_sf_m_in
        self.parameters['vref_sf_m_off'] = vref_sf_m_off
        self.parameters['vref_sf_m_bias_dum'] = vref_sf_m_bias_dum
        self.parameters['vref_sf_m_in_dum'] = vref_sf_m_in_dum
        self.parameters['vref_sf_m_byp'] = vref_sf_m_byp
        self.parameters['vref_sf_m_byp_bias'] = vref_sf_m_byp_bias
        self.parameters['vref_sf_bias_current'] = vref_sf_bias_current
        self.parameters['vref_sf'] = vref_sf
        self.parameters['sar_drv_m_list'] = sar_drv_m_list
        self.parameters['sar_ckgen_m'] = sar_ckgen_m
        self.parameters['sar_ckgen_fo'] = sar_ckgen_fo
        self.parameters['sar_ckgen_ndelay'] = sar_ckgen_ndelay
        self.parameters['sar_ckgen_fast'] = sar_ckgen_fast
        self.parameters['sar_ckgen_muxfast'] = sar_ckgen_muxfast
        self.parameters['sar_logic_m'] = sar_logic_m
        self.parameters['sar_fsm_m'] = sar_fsm_m
        self.parameters['sar_ret_m'] = sar_ret_m
        self.parameters['sar_ret_fo'] = sar_ret_fo
        self.parameters['sar_num_inv_bb'] = sar_num_inv_bb
        self.parameters['sar_device_intent'] = sar_device_intent
        self.parameters['sar_c_m'] = sar_c_m
        self.parameters['sar_rdx_array'] = sar_rdx_array
        self.parameters['samp_lch'] = samp_lch
        self.parameters['samp_wp'] = samp_wp
        self.parameters['samp_wn'] = samp_wn
        self.parameters['samp_fgn'] = samp_fgn
        self.parameters['samp_fg_inbuf_list'] = samp_fg_inbuf_list
        self.parameters['samp_fg_outbuf_list'] = samp_fg_outbuf_list
        self.parameters['samp_nduml'] = samp_nduml
        self.parameters['samp_ndumr'] = samp_ndumr
        self.parameters['samp_nsep'] = samp_nsep
        self.parameters['samp_intent'] = samp_intent
        self.parameters['num_bits'] = num_bits
        self.parameters['samp_tgate'] = samp_tgate
        self.parameters['samp_use_laygo'] = samp_use_laygo #if true, use laygo for sampler generation
        self.parameters['sf_lch'] = sf_lch
        self.parameters['sf_nw'] = sf_nw
        self.parameters['sf_m_mirror'] = sf_m_mirror
        self.parameters['sf_m_bias'] = sf_m_bias
        self.parameters['sf_m_in'] = sf_m_in
        self.parameters['sf_m_off'] = sf_m_off
        self.parameters['sf_m_bias_dum'] = sf_m_bias_dum
        self.parameters['sf_m_in_dum'] = sf_m_in_dum
        self.parameters['sf_m_byp'] = sf_m_byp
        self.parameters['sf_m_byp_bias'] = sf_m_byp_bias
        self.parameters['sf_intent'] = sf_intent
        self.parameters['bias_current'] = bias_current
        self.parameters['use_sf'] = use_sf #if true, source follower is used before the sampler

        self.instances['ISAR0'].design(lch=sar_lch, pw=sar_pw, nw=sar_nw, sa_m=sar_sa_m, sa_m_d=sar_sa_m_d, sa_m_rst=sar_sa_m_rst, sa_m_rst_d=sar_sa_m_rst_d, sa_m_rgnn=sar_sa_m_rgnn, sa_m_rgnp_d=sar_sa_m_rgnp_d, sa_m_buf=sar_sa_m_buf, sa_smallrgnp=sar_sa_m_smallrgnp, doubleSA=doubleSA,
                                       vref_sf_m_mirror=vref_sf_m_mirror, vref_sf_m_bias=vref_sf_m_bias,
                                       vref_sf_m_off=vref_sf_m_off,
                                       vref_sf_m_in=vref_sf_m_in, vref_sf_m_bias_dum=vref_sf_m_bias_dum,
                                       vref_sf_m_in_dum=vref_sf_m_in_dum, vref_sf_m_byp=vref_sf_m_byp,
                                       vref_sf_m_byp_bias=vref_sf_m_byp_bias,
                                       vref_sf_bias_current=vref_sf_bias_current, vref_sf=vref_sf,
                                       drv_m_list=sar_drv_m_list, ckgen_m=sar_ckgen_m, ckgen_fo=sar_ckgen_fo,
                                       ckgen_ndelay=sar_ckgen_ndelay, ckgen_fast=sar_ckgen_fast, ckgen_muxfast = sar_ckgen_muxfast,
                                       logic_m=sar_logic_m,
                                       fsm_m=sar_fsm_m, ret_m=sar_ret_m, ret_fo=sar_ret_fo, c_m=sar_c_m, rdx_array=sar_rdx_array, num_bits=num_bits, num_inv_bb=sar_num_inv_bb,
                                       device_intent=sar_device_intent)
        if samp_use_laygo==True:
            self.replace_instance_master(inst_name='XSAMP0', lib_name='adc_sar_templates', cell_name='sarsamp')
            self.instances['XSAMP0'].design(lch=samp_lch, pw=samp_wp, nw=samp_wn, m_sw=4, m_sw_arr=samp_fgn, m_inbuf_list=samp_fg_inbuf_list, m_outbuf_list=samp_fg_outbuf_list, tgate=samp_tgate, device_intent=samp_intent)
        else:
            self.replace_instance_master(inst_name='XSAMP0', lib_name='adc_ec_templates', cell_name='sampler_nmos')
            self.instances['XSAMP0'].design_specs(lch=samp_lch, wp=samp_wp, wn=samp_wn, fgn=samp_fgn, fg_inbuf_list=samp_fg_inbuf_list, fg_outbuf_list=samp_fg_outbuf_list, nduml=samp_nduml, ndumr=samp_ndumr, nsep=samp_nsep, intent=samp_intent)
            #self.instances['XSAMP0'].design_specs(lch=samp_lch, pw=samp_wp, nw=samp_wn, m_sw=samp_fgn, fg_inbuf_list=samp_fg_inbuf_list, fg_outbuf_list=samp_fg_outbuf_list, nduml=samp_nduml, ndumr=samp_ndumr, nsep=samp_nsep, intent=samp_intent)

        if use_sf == False:
            self.delete_instance('ISF')
            self.remove_pin('SF_bypass')
            self.remove_pin('SF_Voffp')
            self.remove_pin('SF_Voffn')
            self.remove_pin('SF_BIAS')
            self.reconnect_instance_terminal(inst_name='XSAMP0', term_name='inp', net_name='INP')
            self.reconnect_instance_terminal(inst_name='XSAMP0', term_name='inn', net_name='INM')
        else:
            self.instances['ISF'].design(lch=sf_lch, nw=sf_nw, m_mirror=sf_m_mirror, m_bias=sf_m_bias, m_off=sf_m_off,
                                            m_in=sf_m_in, m_bias_dum=sf_m_bias_dum, m_in_dum=sf_m_in_dum, m_byp=sf_m_byp,
                                            m_byp_bias=sf_m_byp_bias, device_intent=sf_intent, bias_current=bias_current)
        if sar_ckgen_muxfast is False:
            self.remove_pin('MODESEL')
        #rewiring
        self.reconnect_instance_terminal(inst_name='XSAMP0', term_name='ckout', net_name='ICLK')
        self.reconnect_instance_terminal(inst_name='XSAMP0', term_name='outp', net_name='SAMPP')
        self.reconnect_instance_terminal(inst_name='XSAMP0', term_name='outn', net_name='SAMPM')
        self.reconnect_instance_terminal(inst_name='ISAR0', term_name='ADCOUT<%d:0>'%(num_bits-1), net_name='ADCOUT<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='ISAR0', term_name='VOL<%d:0>'%(num_bits-2), net_name='VOL<%d:0>'%(num_bits-2))
        self.reconnect_instance_terminal(inst_name='ISAR0', term_name='VOR<%d:0>'%(num_bits-2), net_name='VOR<%d:0>'%(num_bits-2))
        self.reconnect_instance_terminal(inst_name='ISAR0', term_name='ZP<%d:0>'%(num_bits-1), net_name='ZP<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='ISAR0', term_name='ZMID<%d:0>'%(num_bits-1), net_name='ZMID<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='ISAR0', term_name='ZM<%d:0>'%(num_bits-1), net_name='ZM<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='ISAR0', term_name='SB<%d:0>'%(num_bits-1), net_name='SB<%d:0>'%(num_bits-1))
        #rename pins
        self.rename_pin('VOL<0>', 'VOL<%d:0>'%(num_bits-2))
        self.rename_pin('VOR<0>', 'VOR<%d:0>'%(num_bits-2))
        self.rename_pin('ZM<0>', 'ZM<%d:0>'%(num_bits-1))
        self.rename_pin('ZMID<0>', 'ZMID<%d:0>'%(num_bits-1))
        self.rename_pin('ZP<0>', 'ZP<%d:0>'%(num_bits-1))
        self.rename_pin('SB<0>', 'SB<%d:0>'%(num_bits-1))
        self.rename_pin('ADCOUT<0>', 'ADCOUT<%d:0>'%(num_bits-1))

        if vref_sf == False:
            self.remove_pin('VREF_SF_bypass')
            self.remove_pin('VREF_SF_BIAS')

    def get_layout_params(self, **kwargs):
        """Returns a dictionary with layout parameters.

        This method computes the layout parameters used to generate implementation's
        layout.  Subclasses should override this method if you need to run post-extraction
        layout.

        Parameters
        ----------
        kwargs :
            any extra parameters you need to generate the layout parameters dictionary.
            Usually you specify layout-specific parameters here, like metal layers of
            input/output, customizable wire sizes, and so on.

        Returns
        -------
        params : dict[str, any]
            the layout parameters dictionary.
        """
        return {}

    def get_layout_pin_mapping(self):
        """Returns the layout pin mapping dictionary.

        This method returns a dictionary used to rename the layout pins, in case they are different
        than the schematic pins.

        Returns
        -------
        pin_mapping : dict[str, str]
            a dictionary from layout pin names to schematic pin names.
        """
        return {}
