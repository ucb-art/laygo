# LAYGO - LAYout with Gridded Objects

Laygo is an add-on to [BAG2](https://github.com/ucb-art/BAG_framework)
framework for layout generation, written by [Jaeduk Han](https://jdhan.github.io/),
Woorham Bae, Zhongkai Wang, and Eric Jan.
The physical design of analog and mixed-signal (AMS) circuits is very
challenging in advanced CMOS processes, due to their complex design rules.
Laygo abstracts the design rules by introducing quantized templates and
grids. With Laygo, the AMS layout is constructed by placing templates and
routing wires on grids; designers don't need to deal with complex design
rules. Using Laygo, you can script your layout construction process in
Python, which gives higher productivity and process portability over
multiple technology nodes.

![laygo](images/laygo_concept.png)

## Installation and Quick Start
1. Install BAG2 (skip if you are using the GDS flow)
2. Clone laygo repo
    ```
    $ git clone git@github.com:ucb-art/laygo.git
    ```
3. Prepare setup files for your technology.
    * **laygo_config.yaml** - contains general technology information.

        Example: [labs/laygo_config.yaml](https://github.com/ucb-art/laygo/blob/master/labs/laygo_config.yaml)
    * **(technology_name).layermap**(optional) - layer mapping file only
    for the GDS flow. Usually the layermap file can be found in your PDK
    library.

        Example: [labs/laygo_faketech.layermap](https://github.com/ucb-art/laygo/blob/master/labs/laygo_faketech.layermap)
    * **primitive template and grid database** : laygo stores template
    and grid information in yaml files. Users can construct their yaml
    files, or provided from external vendors under NDA.

        Example database files (for laygo_faketech, used in the GDS flow):
        [labs/laygo_faketech_microtemplates_dense_templates.yaml](https://github.com/ucb-art/laygo/blob/master/labs/laygo_faketech_microtemplates_dense_templates.yaml),
        [labs/laygo_faketech_microtemplates_dense_grids.yaml](https://github.com/ucb-art/laygo/blob/master/labs/laygo_faketech_microtemplates_dense_grids.yaml)

        An example script for constructing the yaml database:
        [labs/lab2_a_gridlayoutgenerator_constructtemplate.py](https://github.com/ucb-art/laygo/blob/master/labs/lab2_a_gridlayoutgenerator_constructtemplate.py)

    Example setup files for generic technologies are released for
    reference, which can be found here:

        * [cds_ff_mpt](git@github.com:ucb-art/BAG2_cds_ff_mpt.git)
        * [NCSU FreePDK45](git@github.com:ucb-art/BAG2_freePDK45.git)

    For **BWRC users**, default setup files for various technologies are
    provided under proper NDAs.

4. Let's run a toy example. Launch ipython and run the GDS tutorial script
    [quick_start_GDS.py](https://github.com/ucb-art/laygo/blob/master/quick_start_GDS.py).
    ```
    $ start_bag.sh    (or ipython)
    > cd laygo
    > run quick_start_GDS.py
    ```
    It will create a nand gate layout and save the layout to *output.gds*.

    ![qs_nand](images/laygo_quickstart.png)

    [KLayout](http://www.klayout.de/) was used for the gds display. Detailed
    explanations on the tutorial script are
    [here](https://ucb-art.github.io/laygo/tutorial/tutorial_GDS.html).
    You can also export the layout to the BAG framework. Refer to
    [this document](https://ucb-art.github.io/laygo/tutorial/tutorial_BAG.html)
    for details.

5. For more practice examples, go over lab materials in [labs/](https://github.com/ucb-art/laygo/tree/master/labs).
Detailed instructions can be found in [lab readme](docs/labs.md).

6. More generator examples are being uploaded in [https://ucb-art.github.io/laygo/](https://ucb-art.github.io/laygo/) for reference.

## Documentations
Documents are stored in [https://ucb-art.github.io/laygo/](https://ucb-art.github.io/laygo/).

## Example Labs
Various lab modules are provided to guide the layout generation
procedure. Users are strongly recommended to finish all lab modules
before working on their designs. Labs modules can be found [here](docs/labs.md)

## Example Generators
Example generaters can be found [here](docs/generators.md).

## License
This project is licensed under the BSD License - check the
[LICENSE](LICENSE) file for details.

