def execfile(filepath, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    import os
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)

files=[
    #'laygo/generators/adc_sar/adc_sar_dsn_system.py',
    'laygo/generators/adc_sar/adc_sar_capdac_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_salatch_pmos_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_capdrv_nsw_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_capdrv_nsw_array_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarafe_nsw_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarfsm_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarlogic_wret_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarlogic_wret_array_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarclkdelay_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarclkgen_core_static2_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarclkgen_static_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarret_wckbuf_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_space_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarabe_dualdelay_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sar_layout_generator.py',
    #'laygo/generators/adc_sar/sampler_nmos_layout_generator.py', #for AnalogBase sampler
    'laygo/generators/adc_sar/adc_sar_sarsamp_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sar_wsamp_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sar_wsamp_array_layout_generator.py',
    'laygo/generators/adc_sar/clk_dis_capsw_array_layout_generator.py',
    'laygo/generators/adc_sar/clk_dis_clk_dis_cell_layout_generator.py',
    'laygo/generators/adc_sar/clk_dis_capdac_layout_generator.py',
    'laygo/generators/adc_sar/clk_dis_viadel_cell_layout_generator.py',
    'laygo/generators/adc_sar/clk_dis_viadel_layout_generator.py',
    'laygo/generators/adc_sar/clk_dis_htree_layout_generator.py',
    'laygo/generators/adc_sar/clk_dis_viadel_htree_layout_generator.py',
    'laygo/generators/adc_sar/adc_retimer_layout_generator.py',
    'laygo/generators/adc_sar/tisaradc_body_core_layout_generator.py',
    'laygo/generators/adc_sar/tisaradc_body_core_schematic_generator.py',
    'laygo/generators/adc_sar/tisaradc_body_core_lvs.py',
    ]

for f in files:
    execfile(f)
