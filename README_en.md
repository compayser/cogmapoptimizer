![ITMO Logo](https://gitlab.actcognitive.org/itmo-sai-code/organ/-/raw/main/docs/AIM-Strong_Sign_Norm-01_Colors.svg)

# General information #

The component implements the functions of a strong AI in terms of algorithms for adaptive optimization of production
processes based on intelligent technologies and multi-agent simulation environment in terms of ensuring adaptation
of the simulation environment to various levels of abstraction and details of algorithms due to a combination of cognitive
analysis of the parameters of the production environment and trends in production processes in the oil and gas industry.
The necessary functionality is implemented in the form of the following algorithms:
* algorithm for finding the optimal change in the parameters of the cognitive map;
* multi-agent modeling algorithm.

The component is intended for use in decision support systems when working with complex technical systems.

To use the component, the cognitive map must meet the following conditions:
* the number of vertices of the cognitive map graph (N) is less than 32;
* the number of arcs of the cognitive map graph (M) is less than 992;

# Repository composition #

* [cognitive](cognitive) - agent modeling tool files based on FlameGPU
* [cogmap](cogmap) - cognitive modeling library files
* [docs](docs) - library description [CogMap Optimizer](docs/cogmap_en.md), agent-based modeling programs 
FlameGPU [Cognitive](docs/cognitive_en.md) and examples
* [License GPL v3.0](LICENSE.md)

# Examples of cognitive models and optimization results #
1. Optimizaton [debit wells](docs/example1/Control_example_1_ReadMe_en.md)
2. Liquidation measures [oil spill](docs/example2/Control_example_2_ReadMe_en.md)

# Support #
The study is supported by the Research Center Strong Artificial Intelligence in Industry of ITMO University

