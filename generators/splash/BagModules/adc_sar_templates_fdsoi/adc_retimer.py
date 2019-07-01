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


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'adc_retimer.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__adc_retimer(Module):
    """Module for library adc_sar_templates cell adc_retimer.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, m_ibuf, m_obuf, m_latch, num_slices, num_bits, device_intent='fast'):
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
        for pn, p in zip(['lch', 'pw', 'nw', 'm_ibuf', 'm_obuf', 'num_slices', 'num_bits', 'device_intent'], 
                         [lch, pw, nw, m_ibuf, m_obuf, num_slices, num_bits, device_intent]):
            self.parameters[pn]=p
        #lch=16e-9
        #pw=4
        #nw=4
        #m_ibuf=8
        #m_obuf=8
        #m_latch=2
        #num_slices=8
        #num_bits=9
        #device_intent='fast'
        #clk_bar phases
        #rules:
        # 1) last stage latches: num_slices-1
        # 2) second last stage latches: int(num_slices/2)-1
        # 3) the first half of first stage latches: int((int(num_slices/2)+1)%num_slices)
        # 4) the second half of first stage latches: 1
        # 5) the output phase = the second last latch phase
        ck_phase_2=num_slices-1
        ck_phase_1=int(num_slices/2)-1
        ck_phase_0_0=int((int(num_slices/2)+1)%num_slices)
        ck_phase_0_1=1
        ck_phase_out=ck_phase_1
        ck_phase_buf=sorted(set([ck_phase_2, ck_phase_1, ck_phase_0_0, ck_phase_0_1]))

        #ibuf
        name_list=[]
        term_list=[]
        for i in ck_phase_buf:
            term_list.append({'I': 'clk%d'%(i), 'O':'clkb%d'%(i)})
            name_list.append('IIBUF%d<5:0>'%(i))
        self.array_instance('IIBUF0', name_list, term_list=term_list)
        for inst in self.instances['IIBUF0']:
            inst.design(lch=lch, pw=pw, nw=nw, m=m_ibuf, device_intent=device_intent)

        #obuf
        #self.reconnect_instance_terminal(inst_name='IOBUF0', term_name='I', net_name='clkb%d'%(ck_phase_out))
        self.array_instance('IOBUF0', ['IOBUF0<1:0>'], 
                            term_list=[{'I':'clkb%d'%(ck_phase_out)}])
                            #term_list=[{'I':'in<%d:0>'%(num_bits-1), 'O':'int0<%d:0>'%(num_bits-1)}])
        self.instances['IOBUF0'][0].design(lch=lch, pw=pw, nw=nw, m=m_obuf, device_intent=device_intent)
            
        #slice
        name_list=[]
        term_list=[]
        for i in range(num_slices):
            tdict={'in<%d:0>'%(num_bits-1) : 'in_%d<%d:0>'%(i, num_bits-1), 
                   'out<%d:0>'%(num_bits-1) :'out_%d<%d:0>'%(i, num_bits-1),
                   'clkb2': 'clkb%d'%(ck_phase_2),
                   'clkb1': 'clkb%d'%(ck_phase_1),
                  }
            if i<int(num_slices/2):
                tdict['clkb0']='clkb%d'%(ck_phase_0_0)
            else:
                tdict['clkb0']='clkb%d'%(ck_phase_0_1)
            term_list.append(tdict)
            name_list.append('ISLICE%d'%(i))
        self.array_instance('ISLICE0', name_list, term_list=term_list)
        for inst in self.instances['ISLICE0']:
            inst.design(lch=lch, pw=pw, nw=nw, m=m_latch, num_bits=num_bits, device_intent=device_intent)
    
        pin_in=''
        pin_out=''
        pin_clk=''
        for i in range(num_slices):
            pin_in+='in_%d<%d:0>,'%(i, num_bits-1)
            pin_out+='out_%d<%d:0>,'%(i, num_bits-1)
        for i in ck_phase_buf:
            pin_clk+='clk%d,'%(i)
        pin_in=pin_in[:-1]
        pin_out=pin_out[:-1]
        pin_clk=pin_clk[:-1]
        self.rename_pin('in', pin_in)
        self.rename_pin('out', pin_out)
        self.rename_pin('clk', pin_clk)

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
