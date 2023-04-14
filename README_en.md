[![SAI](https://github.com/ITMO-NSS-team/open-source-ops/blob/master/badges/SAI_badge_flat.svg)](https://sai.itmo.ru/)
[![ITMO](https://github.com/ITMO-NSS-team/open-source-ops/blob/master/badges/ITMO_badge_flat.svg)](https://en.itmo.ru/en/)

[![license](https://img.shields.io/github/license/compayser/cogmapoptimizer)](https://github.com/compayser/cogmapoptimizer/blob/main/LICENSE.md)
[![Eng](https://img.shields.io/badge/lang-ru-yellow.svg)](/README.md)
[![Mirror](https://camo.githubusercontent.com/9bd7b8c5b418f1364e72110a83629772729b29e8f3393b6c86bff237a6b784f6/68747470733a2f2f62616467656e2e6e65742f62616467652f6769746c61622f6d6972726f722f6f72616e67653f69636f6e3d6769746c6162)](https://gitlab.actcognitive.org/itmo-sai-code/cogmapoptimizer)


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
The study is supported by the [Research Center Strong Artificial Intelligence in Industry](https://sai.itmo.ru/) 
of [ITMO University](https://en.itmo.ru/) as part of the plan of the center's program: Development and testing of an experimental prototype of a library of strong AI algorithms in terms of adaptive optimization of production processes based on intelligent technologies, multi-criteria evolutionary schemes and a multi-agent simulation environment.

