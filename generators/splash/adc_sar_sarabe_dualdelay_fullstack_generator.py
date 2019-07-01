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
    'laygo/generators/splash/adc_sar_sarret_wckbuf_size.py',
    'laygo/generators/splash/adc_sar_sarlogic_wret_array_size.py',
    'laygo/generators/splash/adc_sar_sarfsm_size.py',
    'laygo/generators/splash/adc_sar_sarclkgen_static_size.py',
    'laygo/generators/splash/adc_sar_sarfsm_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarlogic_wret_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarlogic_wret_array_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarclkdelay_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarclkgen_core_static2_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarclkgen_static_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarret_wckbuf_layout_generator.py',
    'laygo/generators/splash/adc_sar_space_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarabe_dualdelay_layout_generator.py',
    'laygo/generators/splash/adc_sar_sarabe_dualdelay_schematic_generator.py',
    'laygo/generators/splash/adc_sar_sarabe_dualdelay_lvs.py',
    'laygo/generators/splash/adc_sar_sarabe_dualdelay_extract.py',
    'laygo/generators/splash/adc_sar_sarabe_dualdelay_verify.py',
    ]

for f in files:
    execfile(f)
