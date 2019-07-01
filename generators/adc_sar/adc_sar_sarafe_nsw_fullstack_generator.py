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
    'laygo/generators/adc_sar/adc_sar_capdac_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_salatch_pmos_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_capdrv_nsw_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_capdrv_nsw_array_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarafe_nsw_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarafe_nsw_schematic_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarafe_nsw_lvs.py',
    ]

for f in files:
    execfile(f)
