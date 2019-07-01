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
    'laygo/generators/splash/clk_dis_capsw_array_layout_generator.py',
    'laygo/generators/splash/clk_dis_clk_dis_cell_layout_generator.py',
    'laygo/generators/splash/clk_dis_capdac_layout_generator.py',
    'laygo/generators/splash/clk_dis_viadel_cell_layout_generator.py',
    'laygo/generators/splash/clk_dis_viadel_layout_generator.py',
    'laygo/generators/splash/clk_dis_htree_layout_generator.py',
    'laygo/generators/splash/clk_dis_viadel_htree_layout_generator.py',
    #'laygo/generators/splash/clk_dis_viadel_htree_schematic_generator.py',
    'laygo/generators/splash/clk_dis_viadel_cal_layout.py',
    #'laygo/generators/splash/clk_dis_viadel_cal_schematic.py',
    #'laygo/generators/splash/clk_dis_viadel_htree_lvs.py',
    ]

for f in files:
    execfile(f)
