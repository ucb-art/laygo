# LAYGO - LAYout with Gridded Objects

## Introduction
Laygo is an add-on to [BAG2](https://github.com/ucb-art/BAG_framework)
framework written by [Jaeduk Han](https://jdhan.github.io/), Woorham Bae, 
Zhongkai Wang, and Eric Jan, to generate physical designs (layouts) of 
integrated circuits. Laygo provides various functions and objects to describe 
layout generators, which helps designers produce layouts efficiently in 
advanced CMOS technologies.

To properly abstract the complex design rules in the advanced technologies, 
Laygo introduced quantized templates and grids for its layout generation process;
 the layouts are constructed by placing templates and
routing wires on grids, and designers don't need to deal with complex design
rules. With Laygo, you can easily describe process portable and parameterized 
layout generators in Python, which provide higher productivity and flexibility
to your designs.

![laygo](images/laygo_concept.png)

## Installation and Quick Start
1. Install BAG2 (skip this if you are using the GDS flow).
2. Clone the laygo repository.
    ```
    $ git clone git@github.com:ucb-art/laygo.git
    ```
3. Prepare the following setup files for your technology.
    * **laygo_config.yaml** - contains general technology information.

        An example file can be found here  [labs/laygo_config.yaml](https://github.com/ucb-art/laygo/blob/master/labs/laygo_config.yaml)
    * **(technology_name).layermap** - (optional) layer mapping file only
    for the GDS flow. Usually the layermap file can be found in your PDK
    library.

        An example file can be found here [labs/laygo_faketech.layermap](https://github.com/ucb-art/laygo/blob/master/labs/laygo_faketech.layermap)
    * **primitive template and grid database** : laygo stores template
    and grid information in the YAML format. 

        Example database files (for laygo_faketech, used in the GDS flow):
        [labs/laygo_faketech_microtemplates_dense_templates.yaml](https://github.com/ucb-art/laygo/blob/master/labs/laygo_faketech_microtemplates_dense_templates.yaml),
        [labs/laygo_faketech_microtemplates_dense_grids.yaml](https://github.com/ucb-art/laygo/blob/master/labs/laygo_faketech_microtemplates_dense_grids.yaml)

        An example script for constructing the yaml database:
        [labs/lab2_a_gridlayoutgenerator_constructtemplate.py](https://github.com/ucb-art/laygo/blob/master/labs/lab2_a_gridlayoutgenerator_constructtemplate.py)

    Complete sets of these setup files for generic technologies can be found here:

        [cds_ff_mpt](git@github.com:ucb-art/BAG2_cds_ff_mpt.git)
        [NCSU FreePDK45](git@github.com:ucb-art/BAG2_freePDK45.git)

    **For BWRC users,** default setup files for various technologies are
    provided under proper NDAs.

4. Now you can run a toy example. Launch ipython and run the GDS tutorial script
    [quick_start_GDS.py](https://github.com/ucb-art/laygo/blob/master/quick_start_GDS.py).
    ```
    $ start_bag.sh    (or ipython)
    > cd laygo
    > run quick_start_GDS.py
    ```
    It will create a nand gate layout, and save it to *output.gds*.

    ![qs_nand](images/laygo_quickstart.png)

    [KLayout](http://www.klayout.de/) was used to display the gds. Detailed
    explanations on the tutorial script can be found
    [here](https://ucb-art.github.io/laygo/tutorial/tutorial_GDS.html).
    You can also export the layout to the BAG framework. Check
    [this document](https://ucb-art.github.io/laygo/tutorial/tutorial_BAG.html)
    for the details of the BAG flow.

5. More examples can be found in [labs](https://github.com/ucb-art/laygo/tree/master/labs), 
with [additional documentations](docs/labs.md).

6. Generators of real-world circuits (ADC, SERDES, and so on) are being uploaded in 
[https://ucb-art.github.io/laygo/](https://ucb-art.github.io/laygo/) as well.

## Documentations
More complete documentation can be found here: [https://ucb-art.github.io/laygo/](https://ucb-art.github.io/laygo/).

## Example Labs
Various lab modules are provided to help designers understand the Laygo-based layout 
generation process. Check [this link](docs/labs.md) for details.

## Example Generators
Example generaters can be found [here](docs/generators.md).

## License
This project is licensed under the BSD License - check the
[LICENSE](LICENSE) file for details.

