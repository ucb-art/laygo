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
    'laygo/generators/adc_sar/adc_sar_sarsamp_layout_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarsamp_schematic_generator.py',
    'laygo/generators/adc_sar/adc_sar_sarsamp_lvs.py',
    'laygo/generators/adc_sar/adc_sar_sarsamp_extract.py',
    'laygo/generators/adc_sar/adc_sar_sarsamp_verify.py',
    ]

for f in files:
    execfile(f)
