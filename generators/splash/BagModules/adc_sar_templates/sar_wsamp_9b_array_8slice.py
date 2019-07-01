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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'sar_wsamp_9b_array_8slice.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__sar_wsamp_9b_array_8slice(Module):
    """Module for library adc_sar_templates cell sar_wsamp_9b_array_8slice.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, sar_lch, sar_pw, sar_nw, sar_m_sa, sar_m_rst_sa, sar_m_rgnn_sa, sar_m_buf_sa, sar_m_drv_list, sar_m_ckgen, sar_fo_ckgen, sar_m_ckdly, sar_m_logic, sar_m_fsm, sar_m_ret, sar_fo_ret, sar_device_intent, sar_c_m, sar_rdx_array, samp_lch, samp_wp, samp_wn, samp_fgn, samp_fg_inbuf_list, samp_fg_outbuf_list, samp_nduml, samp_ndumr, samp_nsep, samp_intent):
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
        self.parameters['sar_m_sa'] = sar_m_sa
        self.parameters['sar_m_rst_sa'] = sar_m_rst_sa
        self.parameters['sar_m_rgnn_sa'] = sar_m_rgnn_sa
        self.parameters['sar_m_buf_sa'] = sar_m_buf_sa
        self.parameters['sar_m_drv_list'] = sar_m_drv_list
        self.parameters['sar_m_ckgen'] = sar_m_ckgen
        self.parameters['sar_fo_ckgen'] = sar_fo_ckgen
        self.parameters['sar_m_ckdly'] = sar_m_ckdly
        self.parameters['sar_m_logic'] = sar_m_logic
        self.parameters['sar_m_fsm'] = sar_m_fsm
        self.parameters['sar_m_ret'] = sar_m_ret
        self.parameters['sar_fo_ret'] = sar_fo_ret
        self.parameters['sar_c_m'] = sar_c_m
        self.parameters['sar_rdx_array'] = sar_rdx_array
        self.parameters['sar_device_intent'] = sar_device_intent
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
        for i in range(8):
            iname='ISLICE'+str(i)
            self.instances[iname].design(sar_lch=sar_lch, sar_pw=sar_pw, sar_nw=sar_nw, 
                    sar_m_sa=sar_m_sa, sar_m_rst_sa=sar_m_rst_sa, sar_m_rgnn_sa=sar_m_rgnn_sa, sar_m_buf_sa=sar_m_buf_sa, sar_m_drv_list=sar_m_drv_list, sar_m_ckgen=sar_m_ckgen, 
                    sar_fo_ckgen=sar_fo_ckgen,
                    sar_m_ckdly=sar_m_ckdly, sar_m_logic=sar_m_logic, sar_m_fsm=sar_m_fsm, 
                    sar_m_ret=sar_m_ret, sar_fo_ret=sar_fo_ret, sar_device_intent=sar_device_intent, sar_c_m=sar_c_m, sar_rdx_array=sar_rdx_array,
                    samp_lch=samp_lch, samp_wp=samp_wp, samp_wn=samp_wn, samp_fgn=samp_fgn, 
                    samp_fg_inbuf_list=samp_fg_inbuf_list, samp_fg_outbuf_list=samp_fg_outbuf_list, 
                    samp_nduml=samp_nduml, samp_ndumr=samp_ndumr, samp_nsep=samp_nsep, samp_intent=samp_intent)

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
