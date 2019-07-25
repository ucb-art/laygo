# Laygo Template Library Setup Guide

This section describes how to construct microtemplates_dense library.

## Introduction
The guideline provided in this section is not a golden flow; It is based on my (Woorham Bae's) limited experience, so there must be better solutions.
The intend is just to provide some tips that can reduce number of trials and errors I did.
Just refer and do not rely!

* For now, Laygo does not support ‘path’ drawing, so please use ‘rectangle’ for all routings
* It is hard to get a perfect templates in your first trial. Don’t be frustrated if you cannot make it.
* Best idea is to refer microtemplates_dense library for other technologies if you can access to. 
But you need to understand some basics of template library before you replicate. 

## Let's start with via(wire) template
1) Draw horizontal/vertical metals with minimum width
    * Create => Via => Auto for creating via

    ![template](images/1_via.png)

2) Make the via object a separate instance
    * Edit => Hierarchy => Make cell (ex. via_M1_M2_0)

    ![template](images/2_via_instance.png)

3) Draw other via templates
    * There are various via templates for each layer

    ![template](images/3_via_templates.png)

## Transistor template
* **Nmos4_fast_center_nf2**: Most important templates!

![template](images/4_nmos4_fast_center_nf2.png)

* Before placing an NMOS, we have to decide width (or number of fin) per finger
* Note that two M2 routing can be placed within S/D area

1) Check M2 spacing rule
* With whatever you can do (Options => DRD Options => Enabling DRD Mode is useful) 
![template](images/5_M2_spacing.png)

2) Check V1 spacing rule as well
* Generally it is wider than M1 spacing
* It is not required, just suggested

![template](images/6_V1_spacing.png)

3) Choose number
* Choose a proper number of fins which is available to include two M2 routings/vias and place NMOS
* Turn off poly dummy options: it will be handled later

![template](images/7_unit_width.png)

4) Adjust coordinate of NMOS
* x: Center of left source should be at x=0
* y: Set intuitively(?). Consider a VSS rail will be placed at the bottom. We may modify it later. 

![template](images/8_coordinate.png)

5) Draw gate contact
* One of the hardest part
* Best way is to refer standard cells
* You can activate poly connect option, but…

![template](images/9_gate_contact.png)

* Note that it will be placed in array
* If poly connect option gives a horizontally long M1 connection, you’d better to find an alternate way 

![template](images/10_gate_contact_array.png)

6) Draw additional M1 rectangle
* To meet minimum area requirement for M1
* and to avoid ‘+’ shape when a M1_M2 via is placed
* Again, note that it will be placed in array

![template](images/11_gate_contact_M1.png)

7) Draw some layers (technology dependent)
* Draw some other layers such as finfet and CPO if needed, refer related options embedded in pcell

![template](images/12_final touch.png)

8) Attach pin/label on M1
* Draw M1 pin or label layer on existing M1 drawing layers
    * On gate and every source/drain
    * Choice of pin/label layer depends on technology
* Attach label at the middle of each pin/label layer
    * S0, D0, S1, and G0

![template](images/13_attach_label.png)

* You can specify the pin area with a rectangle of [M1, pin] and net name with a label of [M1, pin] 
* Optionally, you can specify the pin name with a label of  [text, drawing]. This is useful if you want to assign multi pins for same nets.

9) Set boundary
* Use prboundary layer (or corresponding layer) to define the placement boundary of the cell
* Note that one M2 routing will be placed at the top

![template](images/14_set_boundary.png)

* It is recommended to set the height of the template as a common multiples of variety of numbers (i.e. 0.48um, 0.6um…)
* To be compatible with all the routing grids, all placement will be done based on prboundary!

![template](images/15_grid_mismatch.png)

10) Draw pmos4_fast_center_nf2
* It should be very easy if you have drawn nmos4_fast_center_nf2

![template](images/16_pmos4_fast_center_nf2.png)

11) Draw placement_basic
* There is only a prboundary rectangle
* xy0 = (0,0), xy1 = (poly pitch, one of divisions of height of nmos_fast_center_nf2)
    * All x coordinates should be multiples of poly pitch

![template](images/17_placement_basic.png)

## Routing grids

**Draw route_M1_M2_cmos**
* Most important routing grid
* Before drawing that, place nmos and pmos templates

![template](images/18_route_M1_M2_cmos.png)

* 8 horizontal routings within the CMOS template
    * 1 for VDD/VSS rail, 2 for NMOS S/D, 2 for PMOS S/D, 2 for CMOS gate, and 1 for additional gate routing 

![template](images/19_route_M1_M2_cmos.png)

1) Draw prboundary
* xy0 = (0,0), xy1 = (poly pitch, height of cmos)

![template](images/20_prboundary.png)

2) Place M1_M2 vias
* x=0 for all vias, so what you have to do is to set y
* We have already considered that when we drawn nmos, so we can easily find proper y coordinates

![template](images/21_place_M1_M2_vias.png)
    
3) Draw M1/M2 wires
* Make sure your routing grid is compatible with CMOS template
* After that, delete nmos/pmos templates

![template](images/22_draw_M1M2_wires.png)

4) Draw route_M2_M3_cmos
* CMOS-compatible M2_M3 grid is also required
* Just modify M1_M2 vias and M1 rectangle with M2_M3 vias and M3 rectangle from route_M1_M2

![template](images/23_route_M2_M3_cmos.png)

5) Define rest of routing grids
* Draw prboundary: if min. pitch of vertical layer is narrower than PC pitch, x=PC pitch
* else, x=N x PC pitch, where N x PC pitch > min. pitch

![template](images/24_routing_grids.png)

* When we define y grid, we have to consider spacing rule for horizontal layer and height of MOS template
* So basically, y of prboundary is height of MOS

![template](images/25_routing_grids.png)

* After that, all the horizontal routing grid within prboundary should be defined as follows

![template](images/26_routing_grids.png)

* However, if y grid is one of divisions of height of MOS and also meets the spacing rule, a simple template shown below is sufficient 

![template](images/27_routing_grids.png)

## Draw rest of transistor templates
* nf1, stack, dummy, filler, boundary, and tap

![template](images/28_transistor_templates.png)

1) nf1
* nf1_left and nf1_right according to the direction of gate contact
* Consider DRCs for gate connection

![template](images/29_nf1.png)

2) 2stack
* Used for NAND_1x, TINV_1x…
* Utilize gate connection technique you found in nf1 template

![template](images/30_2stack.png)

3) Dummy
* Use center_nf2 template
* Just connect gate-drain and remove pin on the gate

![template](images/31_dummy.png)

4) Space
* For filling space
* Note that RX layer might be included in 4x cell, in order to satisfy RX density rule (not in this layout)

![template](images/32_space.png)

5) Boundary
* Usually, nmos_fast_boundary == space_1x
* boundary_left/right should resolve design rules regarding poly dummy

![template](images/33_boundary.png)

* Number and pattern of poly dummy depends on technology
* Refer dummy option in pcell

![template](images/34_boundary_example.png)

6) Tap
* For connecting body to VDD/VSS

![template](images/35_tap.png)

* Refer to psub/nwell contact provided by foundry
    * Create => Via => Via Definition

![template](images/36_psub_contact.png)

* Two M1s in tap cell
    * VSS M1-pin to both of them
    * TAP0/TAP1 pin using text drawing

![template](images/37_tap_pin.png)