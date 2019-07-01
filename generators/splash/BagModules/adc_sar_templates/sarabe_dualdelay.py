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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'sarabe_dualdelay.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__sarabe_dualdelay(Module):
    """Module for library adc_sar_templates cell sarabe_dualdelay.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, ckgen_m, ckgen_fo, ckgen_ndelay, logic_m, fsm_m, ret_m, ret_fo, num_bits, device_intent='fast'):
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
        self.parameters['lch'] = lch
        self.parameters['pw'] = pw
        self.parameters['nw'] = nw
        self.parameters['num_bits'] = num_bits
        self.parameters['ckgen_m'] = ckgen_m
        self.parameters['ckgen_fo'] = ckgen_fo
        self.parameters['ckgen_ndelay'] = ckgen_ndelay
        self.parameters['logic_m'] = logic_m
        self.parameters['fsm_m'] = fsm_m
        self.parameters['ret_m'] = ret_m
        self.parameters['ret_fo'] = ret_fo
        self.parameters['device_intent'] = device_intent
        self.instances['ICKGEN0'].design(lch=lch, pw=pw, nw=nw, m=ckgen_m, fo=ckgen_fo, ndelay=ckgen_ndelay, device_intent=device_intent)
        self.instances['ISARLOGIC0'].design(lch=lch, pw=pw, nw=nw, m=logic_m, num_bits=num_bits, device_intent=device_intent)
        self.instances['ISARFSM0'].design(lch=lch, pw=pw, nw=nw, m=fsm_m, num_bits=num_bits, device_intent=device_intent)
        self.instances['IRET0'].design(lch=lch, pw=pw, nw=nw, m=ret_m, fo=ret_fo, num_bits=num_bits, device_intent=device_intent)
        self.reconnect_instance_terminal(inst_name='ICKGEN0', term_name='SHORTB', net_name='ZMID<%d>'%(max(0, num_bits-3)))
        self.reconnect_instance_terminal(inst_name='ISARFSM0', term_name='SB<%d:0>'%(num_bits-1), net_name='SB<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='ISARLOGIC0', term_name='SB<%d:0>'%(num_bits-1), net_name='SB<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='ISARLOGIC0', term_name='ZM<%d:0>'%(num_bits-1), net_name='ZM<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='ISARLOGIC0', term_name='ZP<%d:0>'%(num_bits-1), net_name='ZP<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='ISARLOGIC0', term_name='ZMID<%d:0>'%(num_bits-1), net_name='ZMID<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='ISARLOGIC0', term_name='RETO<%d:0>'%(num_bits-1), net_name='RETI<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='IRET0', term_name='IN<%d:0>'%(num_bits-1), net_name='RETI<%d:0>'%(num_bits-1))
        self.reconnect_instance_terminal(inst_name='IRET0', term_name='OUT<%d:0>'%(num_bits-1), net_name='ADCOUT<%d:0>'%(num_bits-1))

        self.rename_pin('ZP<0>','ZP<%d:0>'%(num_bits-1))
        self.rename_pin('ZMID<0>','ZMID<%d:0>'%(num_bits-1))
        self.rename_pin('ZM<0>','ZM<%d:0>'%(num_bits-1))
        self.rename_pin('ADCOUT<0>','ADCOUT<%d:0>'%(num_bits-1))
        self.rename_pin('SB<0>','SB<%d:0>'%(num_bits-1))

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
