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
    'laygo/generators/splash/adc_sar_dsn_system.py',
    'laygo/generators/splash/adc_sar_capdac_layout_generator.py',
    'laygo/generators/splash/adc_sar_salatch_pmos_layout_generator_lvt.py',
    'laygo/generators/splash/adc_sar_capdrv_nsw_layout_generator.py',
    'laygo/generators/splash/adc_sar_capdrv_nsw_array_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarafe_nsw_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarfsm_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarlogic_wret_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarlogic_wret_array_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarclkdelay_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarclkgen_core_static2_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarclkgen_static_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarret_wckbuf_layout_generator.py',
    'laygo/generators/splash/adc_sar_space_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarabe_dualdelay_layout_generator.py',
    'laygo/generators/splash/adc_sar_sar_layout_generator.py',
    #'laygo/generators/splash/sampler_nmos_layout_generator.py', #for AnalogBase sampler
    'laygo/generators/splash/adc_sar_sarsamp_layout_generator.py',
    'laygo/generators/splash/adc_sar_sar_wsamp_schematic_generator.py',
    'laygo/generators/splash/adc_sar_sar_wsamp_layout_generator.py',
    'laygo/generators/splash/adc_sar_sar_wsamp_lvs.py',
    ]

for f in files:
    execfile(f)
