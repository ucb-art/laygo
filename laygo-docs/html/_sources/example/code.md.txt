# Example codes

This section illustrates ways of describing layout generator codes
efficiently. While other examples focus on describing the generation
flow with specific circuit examples (and codes might be outdated),
examples in this section are written in the with the newest APIs and
coding styles, in order to help users to build their codes in the
most effective way. Codes will be kept updated, as new features and
codes added.

## Code example 1: low-level building block generations using primitive templates
This example is about making basic functional elements (i.e. logic gates,
amplifiers) using primitive templates.

[generators/golden/nand_golden_example.py](https://github.com/ucb-art/laygo/blob/master/generators/golden/nand_golden_example.py)

## Code example 2: high-level building block / top generations
This example is about making a block in higher level, composed of basic
elements described in the example 1 (i.e. register files, ADC samplers).

[generators/golden/sarsamp_golden_example.py](https://github.com/ucb-art/laygo/blob/master/generators/golden/sarsamp_golden_example.py)
