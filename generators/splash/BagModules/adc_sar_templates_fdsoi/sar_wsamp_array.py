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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'sar_wsamp_array.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__sar_wsamp_array(Module):
    """Module for library adc_sar_templates cell sar_wsamp_array.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, sar_lch, sar_pw, sar_nw, sar_sa_m, sar_sa_m_rst, sar_sa_m_rgnn, sar_sa_m_buf, sar_drv_m_list, sar_ckgen_m, sar_ckgen_fo, sar_ckgen_ndelay, sar_logic_m, sar_fsm_m, sar_ret_m, sar_ret_fo, sar_device_intent, sar_c_m, sar_rdx_array, samp_lch, samp_wp, samp_wn, samp_fgn, samp_fg_inbuf_list, samp_fg_outbuf_list, samp_nduml, samp_ndumr, samp_nsep, samp_intent, num_bits, samp_use_laygo, num_slices):
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
        self.parameters['sar_sa_m_rst'] = sar_sa_m_rst
        self.parameters['sar_sa_m_rgnn'] = sar_sa_m_rgnn
        self.parameters['sar_sa_m_buf'] = sar_sa_m_buf
        self.parameters['sar_drv_m_list'] = sar_drv_m_list
        self.parameters['sar_ckgen_m'] = sar_ckgen_m
        self.parameters['sar_ckgen_fo'] = sar_ckgen_fo
        self.parameters['sar_ckgen_ndelay'] = sar_ckgen_ndelay
        self.parameters['sar_logic_m'] = sar_logic_m
        self.parameters['sar_fsm_m'] = sar_fsm_m
        self.parameters['sar_ret_m'] = sar_ret_m
        self.parameters['sar_ret_fo'] = sar_ret_fo
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
        self.parameters['samp_use_laygo'] = samp_use_laygo #if true, use laygo for sampler generation
        self.parameters['num_slices'] = num_slices

        #array generation
        name_list=[]
        term_list=[]
        for i in range(num_slices):
            term_list.append({
                'INP': 'INP%d'%(i), 
                'INM': 'INM%d'%(i), 
                'CLK': 'CLK%d'%(i), 
                'OSP': 'OSP%d'%(i), 
                'OSM': 'OSM%d'%(i), 
                'VREF<2:0>': 'VREF<2:0>',
                'CKDSEL0<1:0>': 'ASCLKD%d<1:0>'%(i), 
                'CKDSEL1<1:0>': 'ASCLKD%d<3:2>'%(i), 
                'EXTSEL_CLK' : 'EXTSEL_CLK%d'%(i),
                'ADCOUT<%d:0>'%(num_bits-1) : 'ADCOUT%d<%d:0>'%(i, num_bits-1),
                'CLKO' : 'CLKO%d'%(i),
                'SAMPP' : 'SAMPP%d'%(i),
                'SAMPM' : 'SAMPM%d'%(i),
                'VOL<%d:0>'%(num_bits-2) : 'VOL%d<%d:0>'%(i, num_bits-2),
                'VOR<%d:0>'%(num_bits-2) : 'VOR%d<%d:0>'%(i, num_bits-2),
                'ZP<%d:0>'%(num_bits-1) : 'ZP%d<%d:0>'%(i, num_bits-1),
                'ZMID<%d:0>'%(num_bits-1) : 'ZMID%d<%d:0>'%(i, num_bits-1),
                'ZM<%d:0>'%(num_bits-1) : 'ZM%d<%d:0>'%(i, num_bits-1),
                'SARCLK' : 'SARCLK%d'%(i),
                'SARCLKB' : 'SARCLKB%d'%(i),
                'CLKPRB_SAMP' : 'CLKPRB_SAMP%d'%(i),
                'ICLK' : 'ICLK%d'%(i),
                'DONE' : 'DONE%d'%(i),
                'SB<%d:0>'%(num_bits-1) : 'SB%d<%d:0>'%(i, num_bits-1),
                'UP' : 'UP%d'%(i),
                'PHI0' : 'PHI0_%d'%(i),
                'SAOP' : 'SAOP%d'%(i),
                'SAOM' : 'SAOM%d'%(i),
            })
            name_list.append('ISLICE%d'%(i))
        self.array_instance('ISLICE0', name_list, term_list=term_list)
        for i in range(num_slices):
            self.instances['ISLICE0'][i].design(sar_lch, sar_pw, sar_nw, sar_sa_m, sar_sa_m_rst, sar_sa_m_rgnn, sar_sa_m_buf, sar_drv_m_list, sar_ckgen_m, sar_ckgen_fo, sar_ckgen_ndelay, sar_logic_m, sar_fsm_m, sar_ret_m, sar_ret_fo, sar_device_intent, sar_c_m, sar_rdx_array, samp_lch, samp_wp, samp_wn, samp_fgn, samp_fg_inbuf_list, samp_fg_outbuf_list, samp_nduml, samp_ndumr, samp_nsep, samp_intent, num_bits, samp_use_laygo)
        #rename pins
        pin_enum=['INP', 'INM', 'CLK', 'OSP', 'OSM', 'EXTSEL_CLK', 'CLKO']
        for pn in pin_enum:
            pn_new=''
            for i in range(num_slices):
                pn_new=pn_new+pn+str(i)+','
            pn_new=pn_new[:-1] #remove the last comma
            self.rename_pin(pn+'0', pn_new)
        #rename pins - asclkd
        pn_new=''
        for i in range(num_slices):
            pn_new=pn_new+'ASCLKD'+str(i)+'<3:0>,'
        pn_new=pn_new[:-1] #remove the last comma
        self.rename_pin('ASCLKD0<3:0>', pn_new)
        #rename pins - adcout
        pn_new=''
        for i in range(num_slices):
            pn_new=pn_new+'ADCOUT'+str(i)+'<%d:0>,'%(num_bits-1)
        pn_new=pn_new[:-1] #remove the last comma
        self.rename_pin('ADCOUT0<0>', pn_new)
            
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
