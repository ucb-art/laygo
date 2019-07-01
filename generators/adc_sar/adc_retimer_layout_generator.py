# -*- coding: utf-8 -*-


import bag
from abs_templates_ec.adc_sar.digital.retiming import *
#from abs_templates_ec.adc_sar.digital.retiming import Retimer
from bag.layout import RoutingGrid, TemplateDB
import yaml

impl_lib = 'adc_retimer_ec'
# impl_lib = 'AAAFOO_retimer'

class Retimer2(Retimer):
    """Inherited from abs_templates_ec.adc_sar_digital.retiming
       Added programability on clock phases

    Parameters
    ----------
        temp_db : TemplateDB
            the template database.
    lib_name : str
        the layout library name.
    params : Dict[str, Any]
        the parameter values.
    used_names : Set[str]
        a set of already used cell names.
    **kwargs :
        dictionary of optional parameters.  See documentation of
        :class:`bag.layout.template.TemplateBase` for details.
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        # type: (TemplateDB, str, Dict[str, Any], Set[str], **Any) -> None
        super(Retimer2, self).__init__(temp_db, lib_name, params, used_names, **kwargs)

    @classmethod
    def get_default_param_values(cls):
        # type: () -> Dict[str, Any]
        return dict(reserve_tracks=[])

    @classmethod
    def get_params_info(cls):
        # type: () -> Dict[str, str]
        return dict(
            num_buf='number of clock buffers.',
            num_buf_dig='number of digital clock buffers.',
            num_bits='number of output bits per ADC.',
            num_adc='number of ADCs.',
            adc_width='ADC width in number of columns.',
            cells_per_tap='Number of latch cells per tap connection.',
            config_file='Standard cell configuration file.',
            clk_width='clock wire width.',
            adc_order='List of ADC index order.',
            reserve_tracks='tracks to reserve for ADC routing.',
        )

    def draw_layout(self):
        # type: () -> None

        num_buf = self.params['num_buf']
        num_buf_dig = self.params['num_buf_dig']
        num_bits = self.params['num_bits']
        num_adc = self.params['num_adc']
        adc_width = self.params['adc_width']
        cells_per_tap = self.params['cells_per_tap']
        config_file = self.params['config_file']
        clk_width = self.params['clk_width']
        adc_order = self.params['adc_order']
        reserve_tracks = self.params['reserve_tracks']
        buf_ck_width = 5

        self.set_draw_boundaries(True)

        self.update_routing_grid()

        lat_params = dict(
            parity=0,
            num_bits=num_bits,
            adc_width=adc_width,
            cells_per_tap=cells_per_tap,
            config_file=config_file,
            clk_width=clk_width,
        )
        lat_master0 = self.new_template(params=lat_params, temp_cls=RetimeLatchRow)
        lat_params['parity'] = 1
        lat_master1 = self.new_template(params=lat_params, temp_cls=RetimeLatchRow)

        space_params = dict(
            num_bits=num_bits,
            adc_width=adc_width,
            cells_per_tap=cells_per_tap,
            config_file=config_file,
        )
        space_master = self.new_template(params=space_params, temp_cls=RetimeSpaceRow)
        buf_params = dict(
            num_buf=num_buf,
            num_buf_dig=num_buf_dig,
            num_bits=num_bits,
            adc_width=adc_width,
            cells_per_tap=cells_per_tap,
            config_file=config_file,
        )
        buf_dig_master = self.new_template(params=buf_params, temp_cls=RetimeBufferRow)
        buf_params['num_buf_dig'] = 0
        buf_master = self.new_template(params=buf_params, temp_cls=RetimeBufferRow)
        buf_params['num_buf'] = 0
        buf_fill_master = self.new_template(params=buf_params, temp_cls=RetimeBufferRow)

        spx = lat_master0.std_size[0]
        spy = lat_master0.std_size[1]
        ck_dict = {}

        #finding clock_bar phases <- added by Jaeduk
        #rules:
        # 1) last stage latches: num_adc-1
        # 2) second last stage latches: int(num_adc/2)-1
        # 3) the first half of first stage latches: int((int(num_adc/2)+1)%num_adc)
        # 4) the second half of first stage latches: 1
        # 5) the output phase = the second last latch phase
        ck_phase_2=num_adc-1
        ck_phase_1=int(num_adc/2)-1
        ck_phase_0_0=int((int(num_adc/2)+1)%num_adc)
        ck_phase_0_1=1
        ck_phase_out=ck_phase_1
        ck_phase_buf=sorted(set([ck_phase_2, ck_phase_1, ck_phase_0_0, ck_phase_0_1]))
        print('clocking phases:',ck_phase_2, ck_phase_1, ck_phase_0_0, ck_phase_0_1, ck_phase_out, ck_phase_buf)
        ck_dict[ck_phase_2]=[]
        ck_dict[ck_phase_1]=[]
        ck_dict[ck_phase_0_0]=[]
        ck_dict[ck_phase_0_1]=[]

        # last stage latches
        inst2 = self.add_std_instance(lat_master0, 'X2', nx=num_adc, spx=spx)
        ck_list = inst2.get_all_port_pins('clkb')
        ck_dict[ck_phase_2] += self.connect_wires(ck_list)

        self._export_output(inst2, adc_order, num_bits)
        io_wires = []
        self._collect_io_wires(inst2, 'in', num_bits, io_wires)

        vdd_list = inst2.get_all_port_pins('VDD')
        vss_list = inst2.get_all_port_pins('VSS')

        # second-to-last stage latches
        inst1 = self.add_std_instance(lat_master1, 'X1', loc=(0, spy), nx=num_adc, spx=spx)
        ck_list = inst1.get_all_port_pins('clkb')
        ck_dict[ck_phase_1] += self.connect_wires(ck_list)

        self._collect_io_wires(inst1, 'out', num_bits, io_wires)
        self.connect_wires(io_wires)
        io_wires = []
        self._collect_io_wires(inst1, 'in', num_bits, io_wires)

        vdd_list.extend(inst1.get_all_port_pins('VDD'))
        vss_list.extend(inst1.get_all_port_pins('VSS'))

        # set template size
        cb_nrow = buf_master.std_size[1]
        self.set_std_size((adc_width * num_adc, 4 * spy + cb_nrow))
        # draw boundaries
        self.draw_boundaries()
        blk_w, blk_h = self.grid.get_size_dimension(self.size)

        # first stage latches, clock buffers, and fills
        ck0_1_list = []
        ck0_0_list = []
        buf_dict = {}
        out_dig_warr = None
        for col_idx, adc_idx in enumerate(adc_order):
            if adc_idx < int(num_adc/2):
                finst = self.add_std_instance(space_master, loc=(spx * col_idx, 2 * spy))
                inst = self.add_std_instance(lat_master0, loc=(spx * col_idx, 3 * spy))
                ck_list = ck0_0_list
            else:
                finst = self.add_std_instance(space_master, loc=(spx * col_idx, 3 * spy))
                inst = self.add_std_instance(lat_master0, loc=(spx * col_idx, 2 * spy))
                ck_list = ck0_1_list
            # connect clk/vdd/vss/output
            ck_list.extend(inst.get_all_port_pins('clkb'))
            vdd_list.extend(inst.get_all_port_pins('VDD'))
            vss_list.extend(inst.get_all_port_pins('VSS'))
            vdd_list.extend(finst.get_all_port_pins('VDD'))
            vss_list.extend(finst.get_all_port_pins('VSS'))
            self._collect_io_wires(inst, 'out', num_bits, io_wires)
            # export input
            for bit_idx in range(num_bits):
                in_pin = inst.get_port('in<%d>' % bit_idx).get_pins()[0]
                in_pin = self.connect_wires(in_pin, upper=blk_h)
                name = 'in_%d<%d>' % (adc_idx, bit_idx)
                self.add_pin(name, in_pin, show=True)
            # clock buffers/fills
            #if adc_idx in [1, 3, 5, 7]:
            if adc_idx in ck_phase_buf:
                if adc_idx == ck_phase_out:
                    cur_master = buf_dig_master
                else:
                    cur_master = buf_master
                cfinst = self.add_std_instance(cur_master, loc=(spx * col_idx, 4 * spy))
                vdd_list.extend(cfinst.get_all_port_pins('VDD'))
                vss_list.extend(cfinst.get_all_port_pins('VSS'))
                in_pin = cfinst.get_port('in').get_pins()[0]
                in_pin = self.connect_wires(in_pin, upper=blk_h)
                self.add_pin('clk%d' % adc_idx, in_pin)
                buf_dict[adc_idx] = cfinst.get_port('out').get_pins()[0]
                if cfinst.has_port('out_dig'):
                    out_dig_warr = cfinst.get_port('out_dig').get_pins()[0]
            else:
                cfinst = self.add_std_instance(buf_fill_master, loc=(spx * col_idx, 4 * spy))
                vdd_list.extend(cfinst.get_all_port_pins('VDD'))
                vss_list.extend(cfinst.get_all_port_pins('VSS'))

        self.connect_wires(io_wires)
        ck_dict[ck_phase_0_1] += self.connect_wires(ck0_1_list)
        ck_dict[ck_phase_0_0] += self.connect_wires(ck0_0_list)
        #print(ck_dict)
        #for ck_idx in [1, 3, 5, 7]:
        for ck_idx in ck_phase_buf:
            buf_out = buf_dict[ck_idx]
            buf_layer = buf_out.layer_id
            ck_wires = ck_dict[ck_idx]
            tr_id = self.grid.coord_to_nearest_track(buf_layer + 1, buf_out.middle, mode=0)
            tr_id = TrackID(buf_layer + 1, tr_id, width=buf_ck_width)
            self.connect_to_tracks([buf_out, ] + ck_wires, tr_id, fill_type='')

        # export digital output
        tr_id = self.grid.coord_to_nearest_track(out_dig_warr.layer_id + 1, out_dig_warr.middle, mode=0)
        tr_id = TrackID(out_dig_warr.layer_id + 1, tr_id, width=buf_ck_width)
        warr = self.connect_to_tracks(out_dig_warr, tr_id, fill_type='', track_lower=0)
        self.add_pin('ck_out', warr, show=True)

        sup_layer = vdd_list[0].layer_id + 1
        vdd_list, vss_list = self.do_power_fill(sup_layer, vdd_list, vss_list, sup_width=2,
                                                fill_margin=0.5, edge_margin=0.2)
        sup_layer += 1

        # reserve routing tracks for ADC
        adc_pitch = lat_master0.get_num_tracks(sup_layer)
        for tid in reserve_tracks:
            self.reserve_tracks(sup_layer, tid, num=num_adc, pitch=adc_pitch)

        vdd_list, vss_list = self.do_power_fill(sup_layer, vdd_list, vss_list, sup_width=2,
                                                fill_margin=0.5, edge_margin=0.2)
        sup_layer += 1
        vdd_list, vss_list = self.do_power_fill(sup_layer, vdd_list, vss_list, sup_width=2,
                                                fill_margin=0.5, edge_margin=0.2)

        self.add_pin('VDD', vdd_list, show=True)
        self.add_pin('VSS', vss_list, show=True)

    def _export_output(self, inst, adc_order, num_bits):
        for col_idx, adc_idx in enumerate(adc_order):
            for bit_idx in range(num_bits):
                out_pin = inst.get_port('out<%d>' % bit_idx, col=col_idx).get_pins()[0]
                out_pin = self.connect_wires(out_pin, lower=0)
                name = 'out_%d<%d>' % (adc_idx, bit_idx)
                self.add_pin(name, out_pin, show=True)

    @staticmethod
    def _collect_io_wires(inst, name, num_bits, wire_list):
        for bit_idx in range(num_bits):
            pname = '%s<%d>' % (name, bit_idx)
            wire_list.extend(inst.get_all_port_pins(pname))

def latch_adc(prj, temp_db):
    cell_name = 'adc_retimer'
    layout_params = dict(
        num_buf=3,
        num_buf_dig=1,
        num_bits=9,
        num_adc=8,
        #num_adc=4,
        #num_adc=2,
        adc_width=224,
        cells_per_tap=3,
        config_file='adc_sar_retimer_logic.yaml',
        clk_width=8,
        adc_order=[0, 2, 4, 6, 1, 3, 5, 7],
        #adc_order=[0, 2, 1, 3],
        #adc_order=[0, 1],
        reserve_tracks=[31.5, 38.5, 40.5, 55.5, 57.5, 59.5, 91.5, 93.5,
                        127.5, 129.5, 163.5, 165.5, 229.5, 230.5, 231.5, 232.5],
    )
    #load from preset
    load_from_file=True
    yamlfile_spec="adc_sar_spec.yaml"
    yamlfile_size="adc_sar_size.yaml"
    if load_from_file==True:
        with open(yamlfile_spec, 'r') as stream:
            specdict = yaml.load(stream)
        with open(yamlfile_size, 'r') as stream:
            sizedict = yaml.load(stream)
        layout_params['num_bits']=specdict['n_bit']
        layout_params['num_adc']=specdict['n_interleave']
        layout_params['adc_order']=sizedict['slice_order']
        if layout_params['num_bits']==10: #this is hack; need to be fixed
            layout_params['cells_per_tap']=5
    template = temp_db.new_template(params=layout_params, temp_cls=Retimer2, debug=False)
    #template = temp_db.new_template(params=layout_params, temp_cls=Retimer, debug=False)
    temp_db.instantiate_layout(prj, template, cell_name, debug=True)

    template.write_summary_file('%s.yaml' % cell_name, impl_lib, cell_name)


if __name__ == '__main__':

    local_dict = locals()
    if 'bprj' not in local_dict:
        print('creating BAG project')
        bprj = bag.BagProject()
        temp = 70.0
        layers = [3, 4, 5, 6]
        spaces = [0.058, 0.04, 0.04, 0.112]
        widths = [0.032, 0.04, 0.04, 0.080]
        bot_dir = 'y'

        routing_grid = RoutingGrid(bprj.tech_info, layers, spaces, widths, bot_dir)

        tdb = TemplateDB('template_libs.def', routing_grid, impl_lib, use_cybagoa=True)

        latch_adc(bprj, tdb)
    else:
        print('loading BAG project')
