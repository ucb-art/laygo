# Logic family generator

![logic](images/logic.png)

This section describes how to generate logic gate layout templates,
which are used for constructing custom digital cells.

>Note: the codes are lengthy and not cleaned up yet. An improved 
 version following the tutorial conventions (possibly with more 
abstracting functions) will be released soon.

## Install and launch
1. Clone a proper tech repo. For cds_ff_mpt example type following
commands.

    ```
    $ git clone git@github.com:ucb-art/BAG2_cds_ff_mpt.git
    $ cd BAG2_cds_ff_mpt
    $ git submodule init
    $ git submodule update
    $ git submodule foreach git pull origin master
    ```

2. Set setting up files, run virtuoso and BAG.

3. Run this command to generate logic layouts. The script will create
logic layouts in (tech)_logic_templates library. For example, for
**cds_ff_mpt** technology, the library name will be
**cds_ff_mpt_logic_template**.

    ```python
    run laygo/generators/logic/logic_templates_layout_generator.py
    ```

4. Open (tech)_logic_templates library and check if cells are
generated.

    ![logic_lib](images/logic_lib.png)

## Supported logic gate types

1. bcap : capacitors
2. dcap : decoupling capacitors
3. dff : D flip-flops
4. dff_rsth : D flip-flops with reset high
5. inv : inverters
6. latch_2ck : D latches with differential clock input
7. latch_2ck : D latches with differential clock input, with reset high
8. mux2to1 : 2-to-1 muxes
9. nand : nand gates
10. ndsr : nand-type sr latches
11. nor : nor gates
12. nsw : nmos switches
13. nsw_wovdd : nmos switches without VDD rail
14. oai22 : 2-input oai gates
15. space : fillers
16. space_wovdd : fillers without VDD rail
17. tap : tap cells
18. tap_wovdd : tap cells without vdd rail
19. tgate : transmission gates
20. tie : tie cells
21. tie_wovdd : tie cells without vdd rail
22. tinv : tri-state inverters
23. tinv_small : small tri-state inverters

## Schematic templates

Corresponding schematic templates can be found in:
**generators/logic/logic_templates**.
