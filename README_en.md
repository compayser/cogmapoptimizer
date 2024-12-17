[![SAI](./docs/media/SAI_badge_flat.svg)](https://sai.itmo.ru/)
[![ITMO](./docs/media/ITMO_badge_flat_rus.svg)](https://en.itmo.ru/en/)

[![license](https://img.shields.io/github/license/compayser/cogmapoptimizer)](https://github.com/compayser/cogmapoptimizer/blob/main/LICENSE.md)
[![Eng](https://img.shields.io/badge/lang-en-red.svg)](/README_en.md)

# General information #

An experimental sample of a software library of strong AI algorithms, including non-classical optimization methods for solving problems in conditions of uncertainty and incomplete data, is designed for adaptive optimization of production processes based on intelligent technologies and a multi-agent simulation environment in terms of ensuring the adaptation of the simulation environment to various levels of abstraction and detailing of algorithm execution due to a combination of cognitive analysis of production environment parameters and trends in production processes.
The required functionality is implemented in the form of the following algorithms:
* algorithm for finding the optimal change in cognitive map parameters;
* algorithm for multi-agent modeling.

The component is intended for use in decision support systems when working with complex technical systems.

To use the component, the cognitive map must meet the following conditions:
* the number of vertices of the cognitive map graph (N) is no more than 32;
* the number of cognitive map graph arcs (M) is no more than 992.

# Repository information #

## Repository composition ##

* [cogmap](cogmap) - cognitive modeling library files
* [cognitive](cognitive) - FlameGPU-based agent modeling tool files
* [deploy](deploy) - cognitive map parallel processing tool files
* [ai-interpreter](ai-interpreter) - cognitive map query preparation tool files
* [graph-drawer](graph-drawer) - probabilistic cognitive map visualization tool files
* [docs](docs/README.md) - library description
* [examples](examples/README.md) - examples of cognitive models and optimization results
* [GPL v3.0 License](LICENSE.md)

## Built-in tests ##
Due to the lack of access to the tools and pipeline of CI/CD (continuous integration / continuous deployment) and their settings on the ITMO GitLab side (the "you don't have any active runners" error, the link to the CI/CD settings that leads to the 404 page, etc.), unit testing was carried out in the project's GitHub (https://github.com/compayser/cogmapoptimizer/).

For this, separate requirement files were created:
- requirements.txt - for deployment,
- requirements_test.txt - for testing.

The differences are in the absence of the "wxPython==4.2.2" dependency in the requirements_test.txt file. Firstly, GitHub is unable to install all the software needed to build this library (library files from the Visual C++ Redistributable needed to work with graphics). Secondly, wxPython is not required for the process of unit testing the cognitive modeling and optimization library classes that are the target of testing.

# Support #
The research is supported by the [Research Center for Strong Artificial Intelligence in Industry](https://sai.itmo.ru/) [ITMO University](https://itmo.ru) as part of the center's program event: Technical design and development of an experimental sample of a software library of strong AI algorithms, including non-classical optimization methods for solving problems under conditions of uncertainty and incomplete data.
