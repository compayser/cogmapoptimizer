[![SAI](./docs/media/SAI_badge_flat.svg)](https://sai.itmo.ru/)
[![ITMO](./docs/media/ITMO_badge_flat_rus.svg)](https://en.itmo.ru/en/)

[![license](https://img.shields.io/github/license/compayser/cogmapoptimizer)](https://github.com/compayser/cogmapoptimizer/blob/main/LICENSE.md)
[![Eng](https://img.shields.io/badge/lang-ru-yellow.svg)](/README.md)

# General information #

An experimental sample of a software library of strong AI algorithms, including non-classical optimization methods for solving problems under conditions of uncertainty and incomplete data, is intended for adaptive optimization of production processes based on intelligent technologies and a multi-agent simulation environment in terms of ensuring adaptation of the simulation environment to various levels of abstraction and detailing the execution of algorithms through a combination of cognitive analysis of the parameters of the production environment and trends in production processes.
The necessary functionality is implemented in the form of the following algorithms:
* algorithm for searching for optimal changes in the parameters of the cognitive map;
* multi-agent modeling algorithm.

The component is intended for use in decision support systems when working with complex technical systems.

To use the component, the cognitive map must satisfy the following conditions:
* number of vertices of the cognitive map graph (N) - no more than 32;
* the number of arcs of the cognitive map graph (M) - no more than 992.

# Repository composition #

* [cogmap](cogmap) - cognitive modeling library files
* [cognitive](cognitive) - files of an agent-based modeling tool based on FlameGPU
* [deploy](deploy) - files of cognitive map parallel processing Tool 
* [ai-interpreter](ai-interpreter) - files of tool for preparing cognitive maps AI queries 
* [graph-drawer](graph-drawer) - files of probabilistic cognitive maps visualization tool 
* [docs](docs/README.md) - description of the library
* [examples](examples/README_en.md) - examples of cognitive models and optimization results
* [License GPL v3.0](LICENSE.md)
 
# Support #
The research is supported by the [Research Center Strong Artificial Intelligence in Industry](https://sai.itmo.ru/) of [ITMO University](https://itmo.ru) as part of the center's program event: Technical design and development of an experimental sample of software library of strong AI algorithms, including non-classical optimization methods for solving problems under conditions of uncertainty and incomplete data.
