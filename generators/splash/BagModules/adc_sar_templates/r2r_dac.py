# -*- coding: utf-8 -*-

from typing import Dict

import os
import pkg_resources

from bag.design import Module


yaml_file = pkg_resources.resource_filename(__name__, os.path.join('netlist_info', 'r2r_dac.yaml'))


# noinspection PyPep8Naming
class adc_sar_templates__r2r_dac(Module):
    """Module for library adc_sar_templates cell r2r_dac.

    Fill in high level description here.
    """

    def __init__(self, bag_config, parent=None, prj=None, **kwargs):
        Module.__init__(self, bag_config, yaml_file, parent=parent, prj=prj, **kwargs)

    def design(self, lch, pw, nw, m, num_series, num_bits, device_intent='fast'):
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
        self.parameters['m'] = m
        self.parameters['num_series'] = num_series
        self.parameters['num_bits'] = num_bits
        self.parameters['device_intent'] = device_intent
        # array generation
        name_list = []
        term_list = []
        for i in range(num_bits):
            if i == 0:
                term_list.append({'O': 'out',
                                  'EN': 'EN<%d>' %(num_bits-1-i),
                                  'ENB': 'ENB<%d>' %(num_bits-1-i)
                                  })
            else:
                term_list.append({'O': 'int%d' %(num_bits-i),
                                  'EN': 'EN<%d>' %(num_bits-1-i),
                                  'ENB': 'ENB<%d>' %(num_bits-1-i)
                                  })
            name_list.append('I2RVDD%d' % (num_bits-1-i))
        self.array_instance('I2RVDD', name_list, term_list=term_list)
        for i in range(num_bits):
            self.instances['I2RVDD'][i].design(lch=lch, pw=pw, nw=nw, m=m, num_series=num_series, device_intent=device_intent)
        # array generation
        name_list = []
        term_list = []
        for i in range(num_bits):
            if i == 0:
                term_list.append({'O': 'out',
                                  'EN': 'ENB<%d>' %(num_bits-1-i),
                                  'ENB': 'EN<%d>' %(num_bits-1-i)
                                  })
            else:
                term_list.append({'O': 'int%d' %(num_bits-i),
                                  'EN': 'ENB<%d>' %(num_bits-1-i),
                                  'ENB': 'EN<%d>' %(num_bits-1-i)
                                  })
            name_list.append('I2RVSS%d' % (num_bits-1-i))
        self.array_instance('I2RVSS', name_list, term_list=term_list)
        for i in range(num_bits):
            self.instances['I2RVSS'][i].design(lch=lch, pw=pw, nw=nw, m=m, num_series=num_series, device_intent=device_intent)
        # array generation
        name_list = []
        term_list = []
        for i in range(num_bits):
            if i == 0:
                term_list.append({'I': 'out',
                                  'O': 'int%d' %(num_bits-1-i),
                                  })
            elif i == num_bits-1:
                term_list.append({'I': 'int%d' %(num_bits-i),
                                  'O': 'VSS',
                                  })
            else:
                term_list.append({'I': 'int%d' %(num_bits-i),
                                  'O': 'int%d' %(num_bits-1-i),
                                  })
            if not i == num_bits-1:
                name_list.append('IR%d' % (num_bits-1-i))
            else:
                name_list.append('IR%d' % (num_bits-1-i))
        self.array_instance('IR', name_list, term_list=term_list)
        for i in range(num_bits):
            if i == num_bits-1:
                self.instances['IR'][i].design(lch=lch, pw=pw, nw=nw, m=m, num_series=num_series, device_intent=device_intent)
            else:
                self.instances['IR'][i].design(lch=lch, pw=pw, nw=nw, m=m, num_series=int(num_series/2), device_intent=device_intent)

        # inv array generation
        name_list = []
        term_list = []
        term_list.append({'O': 'ENB<%d:0>' %(num_bits-1),
                          'I': 'SEL<%d:0>' %(num_bits-1),
                          })
        name_list.append('IINV0<%d:0>' %(num_bits-1))
        self.array_instance('IINV0', name_list, term_list=term_list)
        self.instances['IINV0'][0].design(lch=lch, pw=pw, nw=nw, m=2, device_intent=device_intent)

        name_list = []
        term_list = []
        term_list.append({'O': 'EN<%d:0>' %(num_bits-1),
                          'I': 'ENB<%d:0>' %(num_bits-1),
                          })
        name_list.append('IINV1<%d:0>' %(num_bits-1))
        self.array_instance('IINV1', name_list, term_list=term_list)
        self.instances['IINV1'][0].design(lch=lch, pw=pw, nw=nw, m=2, device_intent=device_intent)

        self.rename_pin('SEL', 'SEL<%d:0>' % (num_bits - 1))
        # self.rename_pin('ZP<0>', 'ZP<%d:0>' % (num_bits - 1))
        # self.rename_pin('ZMID<0>', 'ZMID<%d:0>' % (num_bits - 1))
        # self.rename_pin('ZM<0>', 'ZM<%d:0>' % (num_bits - 1))
        # self.rename_pin('RETO<0>', 'RETO<%d:0>' % (num_bits - 1))
        #
        # name_list_p = []
        # name_list_n = []
        # term_list = []
        # for i in range(num_bits):
        #     for j in range(num_inv_bb):
        #         if j == (num_inv_bb - 1):
        #             term_list.append({'G': 'ZP%d' % (j) + '<%d>' % (i),
        #                               'D': 'ZP<%d>' % (i),
        #                               })
        #         else:
        #             term_list.append({'G': 'ZP%d' % (j) + '<%d>' % (i),
        #                               'D': 'ZP%d' % (j + 1) + '<%d>' % (i),
        #                               })
        #         name_list_p.append('IBUFP0%d' % (j) + '<%d>' % (i))
        #         name_list_n.append('IBUFN0%d' % (j) + '<%d>' % (i))
        # self.array_instance('IBUFP0', name_list_p, term_list=term_list)
        # self.array_instance('IBUFN0', name_list_n, term_list=term_list)
        # for i in range(num_bits * num_inv_bb):
        #     self.instances['IBUFP0'][i].design(w=pw, l=lch, nf=m, intent=device_intent)
        #     self.instances['IBUFN0'][i].design(w=pw, l=lch, nf=m, intent=device_intent)
        # name_list_p = []
        # name_list_n = []
        # term_list = []
        # for i in range(num_bits):
        #     for j in range(num_inv_bb):
        #         if j == (num_inv_bb - 1):
        #             term_list.append({'G': 'ZMID%d' % (j) + '<%d>' % (i),
        #                               'D': 'ZMID<%d>' % (i),
        #                               })
        #         else:
        #             term_list.append({'G': 'ZMID%d' % (j) + '<%d>' % (i),
        #                               'D': 'ZMID%d' % (j + 1) + '<%d>' % (i),
        #                               })
        #         name_list_p.append('IBUFP1%d' % (j) + '<%d>' % (i))
        #         name_list_n.append('IBUFN1%d' % (j) + '<%d>' % (i))
        # self.array_instance('IBUFP1', name_list_p, term_list=term_list)
        # self.array_instance('IBUFN1', name_list_n, term_list=term_list)
        # for i in range(num_bits * num_inv_bb):
        #     self.instances['IBUFP1'][i].design(w=pw, l=lch, nf=m, intent=device_intent)
        #     self.instances['IBUFN1'][i].design(w=pw, l=lch, nf=m, intent=device_intent)
        # name_list_p = []
        # name_list_n = []
        # term_list = []
        # for i in range(num_bits):
        #     for j in range(num_inv_bb):
        #         if j == (num_inv_bb - 1):
        #             term_list.append({'G': 'ZM%d' % (j) + '<%d>' % (i),
        #                               'D': 'ZM<%d>' % (i),
        #                               })
        #         else:
        #             term_list.append({'G': 'ZM%d' % (j) + '<%d>' % (i),
        #                               'D': 'ZM%d' % (j + 1) + '<%d>' % (i),
        #                               })
        #         name_list_p.append('IBUFP2%d' % (j) + '<%d>' % (i))
        #         name_list_n.append('IBUFN2%d' % (j) + '<%d>' % (i))
        # self.array_instance('IBUFP2', name_list_p, term_list=term_list)
        # self.array_instance('IBUFN2', name_list_n, term_list=term_list)
        # for i in range(num_bits * num_inv_bb):
        #     self.instances['IBUFP2'][i].design(w=pw, l=lch, nf=m, intent=device_intent)
        #     self.instances['IBUFN2'][i].design(w=pw, l=lch, nf=m, intent=device_intent)

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