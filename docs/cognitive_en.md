# Simulation of specified pulse processes in the FLAME GPU environment #

The program is based on input files - cognitive map (input_map.cmj), simulation parameter tracking settings (input_group.cmj_xyz), simulation runtime configuration file (config.txt ). In the process, the program code of the model is generated and the initial iteration is performed in the FLAME GPU environment. After running the model in the FLAME GPU environment, it is possible to generate a report based on the received iterative data - a text file with a list of monitored vertices, and checking each for entering the acceptable range.

### The composition of the project ###

| File		| Purpose				 |
|---------------|----------------------------------------|
| cognitive.cpp	| calling the model, analyzing input parameters|
| model.cpp	| generating a model project             |
| model.h       |                                        |
| nxjson.cpp    | JSON format parsing			 |
| nxjson.h      |                                        |
| Makefile      | build script				 |
| make.sh       |                                        |
| prj_templates/ | templates for generating a model project
| prj_templates/Makefile | |
| prj_templates/make.sh | |
| prj_templates/run.sh | |
| src/model/XMlModelFile.xml | |
| src/model/functions.c | |

### Building a project###

The project is built using a script make.sh . g++ 7.5.0 compiler in Ubuntu 18.04 operating environment.
As a result of the build, the executable file *cognitive* appears

### Configuration file format config.txt ###

Contains the following data line by line:

* project name
* availability of built-in visualization
* path to FLAME GPU
* path to the FLAME GPU project folder
* number of iterations

Cognitive map input file:

*test.cmj* - a file in JSON format describing the cognitive map and input impulses

Tuning file of delays for pulses *impulse-lag.txt*:

For each vertex in order, the delay value is in a separate line

### Format and order of starting the model generator ###

Examples and the procedure for launching the program are given in the script run.sh

*Generating the model source code:*
```
./cognitive --project test.cmj group.cmj_xyz
```
At this stage, we get the generation of the model code in the folder specified in the configuration file (the path to the folder with FLAME GPU projects). The name of the resulting model is cognitiv-task.

*Generation of the zero iteration of the model:*
```
./cognitive --generate test.cmj group.cmj_xyz
```
The result is an input xml file for modeling, in which the connections between the vertices, the values in the vertices, the monitored vertices and other settings are specified.
*Assembling the model in the FLAME GPU environment:*
```
./cognitive --make test.cmj group.cmj_xyz
```
Runs the generated model project compilation script for FLAME GPU. The result is a compiled binary file of the model.

*Running the model in the FLAME GPU environment:*
```
./cognitive --run test.cmj group.cmj_xyz
```
Launch on project modeling. The result is xml files (1.xml , 2.xml ...) with a description of the state at each step of the simulation iteration.

*Analysis of the obtained iterative data:*
```
./cognitive --analize test.cmj group.cmj_xyz
```
Generates a final report in text form based on input files with iterative data obtained in the previous step. An example of such a report is given below.


### Sample report ###

Report text:

	Monitored vertexes:
	Vertex: 1669816232058, Testable range:[1.800000-5.000000]
		Iterations where the value does not fall within the acceptable range:
			1 
		Iterations where the value falls within the acceptable range:
			2 3 4 5 6 

The vertex ID corresponds to the ID specified in the input file of the cognitive map. The number of iterations is set in the input configuration file and must correspond to the number of iterations on the basis of which the input data is generated.
