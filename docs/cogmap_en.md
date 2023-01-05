# CogMap #
The library contains a set of classes that provide adaptive optimization using
cognitive modeling.

# Usage example #

Below is an example of connecting and using the CogMap Optimizer library . 

```python
import sys
from pathlib import Path
import cogmap as cm
import impact_generator as ig
import report
from optimizer import Optimizer


if __name__ == '__main__':
    # input data - cognitive map file, vertex group file, number of pulse modeling steps
    if len(sys.argv) < 4:
        print("usage %s <input.cmj> <input.xyz_cmj> <pulse model steps>", sys.argv[0])
        exit(-1)

    cogmap_json_path = sys.argv[1]
    cogmap_xyz_json_path = sys.argv[2]
    N = int(sys.argv[3])

    optimizer = Optimizer()
    simple_structs = optimizer.get_simple_structs()
    impactgen = ig.ImpactGenerator()

    # reading the cognitive map configuration and input data
    print("Loading config...")
    with open(cogmap_json_path, "r") as config_file:
        cogmap_json = config_file.read()
    with open(cogmap_xyz_json_path, "r") as config_xyz_file:
        cogmap_xyz_json = config_xyz_file.read()
    base_cogmap = cm.CogMap()
    base_cogmap.fill_from_json(cogmap_json, cogmap_xyz_json)
    print("Analyzing...")
    res, data = optimizer.find_optimal_changes(base_cogmap, N, simple_structs, impactgen)
    if res == -1:
        print("Problems not found")
        exit(0)
    if res == 0:
        print("Solutions not found")
        exit(0)

    i = 0
    print("Built %d composition(s)" % len(data))
    print("Building reports...")
    p = Path(cogmap_json_path)

    for d in data:
        r = report.Report(d)
        result_dir = str(p.parent) + "\\added_%d" % d.added_new_vertices
        rd = Path(result_dir)
        if not rd.exists():
            rd.mkdir()
        result_filename = str(result_dir) + "\\" + p.name + ".out%d.cmj" % i
        i = i + 1
        r.save_to_file(result_filename)
    print("Done")
```


# File cogmap.py #
## Class Impulses ##
    Describes a series of impulses (impacts) on the cognitive map

## Class Vertex ##
    Describes the vertex of the cognitive map

## Class Edge ##
    Describes the edge of the cognitive map

## Class CogMap ##
    Describes a cognitive map
    __init__(self, vertices=[], edges=[]):
        Designer
        vertices - array of vertices
        edged - array of edges

    is_stable(self)
	Returns True if the cognitive map is stable (combines checking for structural adaptability and
resistance to disturbances)

    fill_from_json(self, data, data_xyz)
	Fills in cognitive map data from data in JSON format
        data - description of the cognitive map
        data_xyz - description of the vertex groups of the cognitive map

    vertex_idx_by_id(self, id)
	Returns the index of a vertex by its identifier
        id - vertex identifier

    rebuild_indexes(self)
        Rebuilds the index tables of the vertices and edges of the cognitive map

    rebuild_matrix(self)
        Rebuilds the adjacency matrix according to arrays of vertices and edges

    add_vertex(self, v)
        Adds a vertex
        v - vertex

    add_edge(self, e)
        Adds an edge
        e - edge

    rem_vertex(self, id)
        Deletes a vertex
        id - vertex ID

    rem_edge(self, id)
        Removes an edge
        id - edge ID

    rem_edge_by_vertices(self, v1_id, v2_id)
        Удаляет ребро
        v1_id - vertex ID 1
        v2_id - vertex ID 2
    
    pulse_calc(self, qq, vvq, st)
       Analysis of trends in the development of situations on the cognitive model - impulse modeling
        qq - pulse values
        vvq - pulse vertex indexes
        st - number of modeling steps

    eig_vals_calc(self, ar)
	Determination of the stability of the system to disturbances
        ar - adjacency matrix

    def simplex_calc(self, v):

    def cycles_calc(self, ar)
	Definitions of structural stability
        ar - adjacency matrix

    sy1(self, ar, vc)
	simplex calculation for a single vertex
        ar - adjacency matrix
        vc - vertex index

    sy(self, ar)
        gives simplicial complexes of the corresponding order and q-connectivity between them, dimension 
        q-connectivity = the number of vertices with which it is connected minus 1 because the presence of only the 1st connection
        indicates a zero order of connectivity
    
    get_composition(self, s1, vk, vs, use)
        Determining the composition of the selected simple structure
        s1 - the matrix of the piece that we add to the system, a segment, a triangle, a square, a clock, etc.
        vk - this is a list of vertices of the original matrix k1 on which the complement is attached
        vs - this is a list of vertices of the original matrix of the piece s1 that are to be attached
        use - the flag of the complement method of the original matrix, 0 or 1 - regulates the behavior of combining edges if there are any
	Returns a CogMap instance with updated lists of vertices and edges
    comboV(self, k1, s1, vk, vs, use)
	Determining the composition of the selected simple structure
        k1 - this is the original matrix of the graph, the current state of the system
        s1 - the matrix of the piece that we add to the system, a segment, a triangle, a square, a clock, etc.
        vk - this is a list of vertices of the original matrix k1 on which the complement is attached
        vs - this is a list of vertices of the original matrix of the piece s1 which are to be attached
        use - flag of the complement method of the original matrix, 0 or 1 - regulates the behavior of combining edges if there are any
	Returns the adjacency matrix

    pulse_model(self, N, impulses=None)
        Analysis of trends in the development of situations on the cognitive model - impulse modeling
        N - number of modeling steps
        impulses - impulses (if not specified - are filled in based on the cognitive map data received from their file when downloading)
	Returns vertex values

    get_neighbors(self, vertex_idx: int, deep: int)
	Returns a list of neighboring vertices within the specified search depth
        vertex_idx - index of the original vertex
        deep - search depth

    get_compositions(self, s, vertex: Vertex)
       Returns a list of all compositions of a given vertex and its surroundings with a simple structure
        vertex - initial vertex
        s - adjacency matrix of a simple structure


# File optimizer.py #
## Класс SolutionData ##
    Data solutions

## Class Optimizer ##
    get_simple_structs(self)
	Returns a list of available simple structures

    find_impact(self, cogmap: cm.CogMap, V: list[cm.Vertex], N: int, impactgen: ig.ImpactGenerator, initial_impulses: list[float]=None)
        Selects the impact to correct the condition
        cogmap - coginitive map
        V - list of vertices to impact
        N - number of pulse simulation steps
        impactgen - impact generator
        initial_impulses - initial impacts (for search)

    mix_solutions(self, base_cogmap: cm.CogMap, solutions: list[SolutionData])
        Forms the composition of solutions
        base_cogmap - basic cognitive map
        solutions - list of solutions

    build_compositions(self, base_cogmap: cm.CogMap, partial_solutions: list[SolutionData])
    	Generates a list of compositions of solutions
        base_cogmap - basic cognitive map
        partial_solutions - list of private solutions

    process_simple_structs(self, cogmap: cm.CogMap, s, vertex: cm.Vertex, impactgen: ig.ImpactGenerator, old_v_bad, old_max_y_er)
        Forms solutions based on compositions with a given simple structure
        cogmap - cognitive map
        s - simple structure
        vertex - target vertex
        impactgen - impact generator
        old_v_bad - initial list of "bad" vertices
        old_max_y_er - the initial value of the deviation of "bad" vertices

    find_optimal_changes(self, base_cogmap: cm.CogMap, N: int, simple_structs: list[list[float]], impactgen: ig.ImpactGenerator)
        base_cogmap - basic cognitive map
        N - number of pulse simulation steps
        simple_structs - list of simple structures
        impactgen - impact generator

# File impact_generator.py #
## Class ImpactData ##
    Impact data

## Class ImpactGenerator ##
    add_impact(self, impact: ImpactData)
        Adds an impact to the impact retrospective
        impact - impact data

    get_impact(self, cogmap, V: list[cm.Vertex])
       Returns the impact for a given cognitive map and vertices
        cogmap - cognitive map
        V - list of vertices

# File report.py #
## Class Report ##
    Report Generator
    __init__(self, data)
        Designer
        data - data for the report

    build_report(self)
        Generates a report in JSON format

    save_to_file(self, filename)
	Writes the report to a file
        filename - file name