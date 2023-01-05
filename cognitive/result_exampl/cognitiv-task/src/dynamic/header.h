
/*
 * FLAME GPU v 1.5.X for CUDA 9
 * Copyright University of Sheffield.
 * Original Author: Dr Paul Richmond (user contributions tracked on https://github.com/FLAMEGPU/FLAMEGPU)
 * Contact: p.richmond@sheffield.ac.uk (http://www.paulrichmond.staff.shef.ac.uk)
 *
 * University of Sheffield retain all intellectual property and
 * proprietary rights in and to this software and related documentation.
 * Any use, reproduction, disclosure, or distribution of this software
 * and related documentation without an express license agreement from
 * University of Sheffield is strictly prohibited.
 *
 * For terms of licence agreement please attached licence or view licence
 * on www.flamegpu.com website.
 *
 */



#ifndef __HEADER
#define __HEADER

#if defined(__NVCC__) && defined(__CUDACC_VER_MAJOR__) && __CUDACC_VER_MAJOR__ >= 9
   // Disable annotation on defaulted function warnings (glm 0.9.9 and CUDA 9.0 introduced this warning)
   #pragma diag_suppress esa_on_defaulted_function_ignored 
#endif

#define GLM_FORCE_NO_CTOR_INIT
#include <glm/glm.hpp>

/* General standard definitions */
//Threads per block (agents per block)
#define THREADS_PER_TILE 64
//Definition for any agent function or helper function
#define __FLAME_GPU_FUNC__ __device__
//Definition for a function used to initialise environment variables
#define __FLAME_GPU_INIT_FUNC__
#define __FLAME_GPU_STEP_FUNC__
#define __FLAME_GPU_EXIT_FUNC__
#define __FLAME_GPU_HOST_FUNC__ __host__

#define USE_CUDA_STREAMS
#define FAST_ATOMIC_SORTING

// FLAME GPU Version Macros.
#define FLAME_GPU_MAJOR_VERSION 1
#define FLAME_GPU_MINOR_VERSION 5
#define FLAME_GPU_PATCH_VERSION 0

typedef unsigned int uint;

//FLAME GPU vector types float, (i)nteger, (u)nsigned integer, (d)ouble
typedef glm::vec2 fvec2;
typedef glm::vec3 fvec3;
typedef glm::vec4 fvec4;
typedef glm::ivec2 ivec2;
typedef glm::ivec3 ivec3;
typedef glm::ivec4 ivec4;
typedef glm::uvec2 uvec2;
typedef glm::uvec3 uvec3;
typedef glm::uvec4 uvec4;
typedef glm::dvec2 dvec2;
typedef glm::dvec3 dvec3;
typedef glm::dvec4 dvec4;

	

/* Agent population size definitions must be a multiple of THREADS_PER_TILE (default 64) */
//Maximum buffer size (largest agent buffer size)
#define buffer_size_MAX 1048576

//Maximum population size of xmachine_memory_vertice
#define xmachine_memory_vertice_MAX 1048576 
//Agent variable array length for xmachine_memory_vertice->edges
#define xmachine_memory_vertice_edges_LENGTH 17


  
  
/* Message population size definitions */
//Maximum population size of xmachine_mmessage_send_local
#define xmachine_message_send_local_MAX 1048576


/* Define preprocessor symbols for each message to specify the type, to simplify / improve portability */

#define xmachine_message_send_local_partitioningNone

/* Spatial partitioning grid size definitions */

/* Static Graph size definitions*/
  

/* Default visualisation Colour indices */
 
#define FLAME_GPU_VISUALISATION_COLOUR_BLACK 0
#define FLAME_GPU_VISUALISATION_COLOUR_RED 1
#define FLAME_GPU_VISUALISATION_COLOUR_GREEN 2
#define FLAME_GPU_VISUALISATION_COLOUR_BLUE 3
#define FLAME_GPU_VISUALISATION_COLOUR_YELLOW 4
#define FLAME_GPU_VISUALISATION_COLOUR_CYAN 5
#define FLAME_GPU_VISUALISATION_COLOUR_MAGENTA 6
#define FLAME_GPU_VISUALISATION_COLOUR_WHITE 7
#define FLAME_GPU_VISUALISATION_COLOUR_BROWN 8

/* enum types */

/**
 * MESSAGE_OUTPUT used for all continuous messaging
 */
enum MESSAGE_OUTPUT{
	single_message,
	optional_message,
};

/**
 * AGENT_TYPE used for templates device message functions
 */
enum AGENT_TYPE{
	CONTINUOUS,
	DISCRETE_2D
};


/* Agent structures */

/** struct xmachine_memory_vertice
 * continuous valued agent
 * Holds all agent variables and is aligned to help with coalesced reads on the GPU
 */
struct __align__(16) xmachine_memory_vertice
{
    int id;    /**< X-machine memory variable id of type int.*/
    float value;    /**< X-machine memory variable value of type float.*/
    float add_value;    /**< X-machine memory variable add_value of type float.*/
    float previous;    /**< X-machine memory variable previous of type float.*/
    int max_lag;    /**< X-machine memory variable max_lag of type int.*/
    int current_lag;    /**< X-machine memory variable current_lag of type int.*/
    float *edges;    /**< X-machine memory variable edges of type float.*/
    float min;    /**< X-machine memory variable min of type float.*/
    float max;    /**< X-machine memory variable max of type float.*/
    int need_test;    /**< X-machine memory variable need_test of type int.*/
    int correct;    /**< X-machine memory variable correct of type int.*/
};



/* Message structures */

/** struct xmachine_message_send_local
 * Brute force: No Partitioning
 * Holds all message variables and is aligned to help with coalesced reads on the GPU
 */
struct __align__(16) xmachine_message_send_local
{	
    /* Brute force Partitioning Variables */
    int _position;          /**< 1D position of message in linear message list */   
      
    int from_id;        /**< Message variable from_id of type int.*/  
    float value;        /**< Message variable value of type float.*/
};



/* Agent lists. Structure of Array (SoA) for memory coalescing on GPU */

/** struct xmachine_memory_vertice_list
 * continuous valued agent
 * Variables lists for all agent variables
 */
struct xmachine_memory_vertice_list
{	
    /* Temp variables for agents. Used for parallel operations such as prefix sum */
    int _position [xmachine_memory_vertice_MAX];    /**< Holds agents position in the 1D agent list */
    int _scan_input [xmachine_memory_vertice_MAX];  /**< Used during parallel prefix sum */
    
    int id [xmachine_memory_vertice_MAX];    /**< X-machine memory variable list id of type int.*/
    float value [xmachine_memory_vertice_MAX];    /**< X-machine memory variable list value of type float.*/
    float add_value [xmachine_memory_vertice_MAX];    /**< X-machine memory variable list add_value of type float.*/
    float previous [xmachine_memory_vertice_MAX];    /**< X-machine memory variable list previous of type float.*/
    int max_lag [xmachine_memory_vertice_MAX];    /**< X-machine memory variable list max_lag of type int.*/
    int current_lag [xmachine_memory_vertice_MAX];    /**< X-machine memory variable list current_lag of type int.*/
    float edges [xmachine_memory_vertice_MAX*17];    /**< X-machine memory variable list edges of type float.*/
    float min [xmachine_memory_vertice_MAX];    /**< X-machine memory variable list min of type float.*/
    float max [xmachine_memory_vertice_MAX];    /**< X-machine memory variable list max of type float.*/
    int need_test [xmachine_memory_vertice_MAX];    /**< X-machine memory variable list need_test of type int.*/
    int correct [xmachine_memory_vertice_MAX];    /**< X-machine memory variable list correct of type int.*/
};



/* Message lists. Structure of Array (SoA) for memory coalescing on GPU */

/** struct xmachine_message_send_local_list
 * Brute force: No Partitioning
 * Structure of Array for memory coalescing 
 */
struct xmachine_message_send_local_list
{
    /* Non discrete messages have temp variables used for reductions with optional message outputs */
    int _position [xmachine_message_send_local_MAX];    /**< Holds agents position in the 1D agent list */
    int _scan_input [xmachine_message_send_local_MAX];  /**< Used during parallel prefix sum */
    
    int from_id [xmachine_message_send_local_MAX];    /**< Message memory variable list from_id of type int.*/
    float value [xmachine_message_send_local_MAX];    /**< Message memory variable list value of type float.*/
    
};



/* Spatially Partitioned Message boundary Matrices */



/* Graph structures */


/* Graph Edge Partitioned message boundary structures */


/* Graph utility functions, usable in agent functions and implemented in FLAMEGPU_Kernels */


  /* Random */
  /** struct RNG_rand48
  *	structure used to hold list seeds
  */
  struct RNG_rand48
  {
  glm::uvec2 A, C;
  glm::uvec2 seeds[buffer_size_MAX];
  };


/** getOutputDir
* Gets the output directory of the simulation. This is the same as the 0.xml input directory.
* @return a const char pointer to string denoting the output directory
*/
const char* getOutputDir();

  /* Random Functions (usable in agent functions) implemented in FLAMEGPU_Kernels */

  /**
  * Templated random function using a DISCRETE_2D template calculates the agent index using a 2D block
  * which requires extra processing but will work for CONTINUOUS agents. Using a CONTINUOUS template will
  * not work for DISCRETE_2D agent.
  * @param	rand48	an RNG_rand48 struct which holds the seeds sued to generate a random number on the GPU
  * @return			returns a random float value
  */
  template <int AGENT_TYPE> __FLAME_GPU_FUNC__ float rnd(RNG_rand48* rand48);
/**
 * Non templated random function calls the templated version with DISCRETE_2D which will work in either case
 * @param	rand48	an RNG_rand48 struct which holds the seeds sued to generate a random number on the GPU
 * @return			returns a random float value
 */
__FLAME_GPU_FUNC__ float rnd(RNG_rand48* rand48);

/* Agent function prototypes */

/**
 * send_message FLAMEGPU Agent Function
 * @param agent Pointer to an agent structure of type xmachine_memory_vertice. This represents a single agent instance and can be modified directly.
 * @param send_local_messages Pointer to output message list of type xmachine_message_send_local_list. Must be passed as an argument to the add_send_local_message function ??.* @param rand48 Pointer to the seed list of type RNG_rand48. Must be passed as an argument to the rand48 function for generating random numbers on the GPU.
 */
__FLAME_GPU_FUNC__ int send_message(xmachine_memory_vertice* agent, xmachine_message_send_local_list* send_local_messages, RNG_rand48* rand48);

/**
 * read_message FLAMEGPU Agent Function
 * @param agent Pointer to an agent structure of type xmachine_memory_vertice. This represents a single agent instance and can be modified directly.
 * @param send_local_messages  send_local_messages Pointer to input message list of type xmachine_message__list. Must be passed as an argument to the get_first_send_local_message and get_next_send_local_message functions.* @param rand48 Pointer to the seed list of type RNG_rand48. Must be passed as an argument to the rand48 function for generating random numbers on the GPU.
 */
__FLAME_GPU_FUNC__ int read_message(xmachine_memory_vertice* agent, xmachine_message_send_local_list* send_local_messages, RNG_rand48* rand48);

  
/* Message Function Prototypes for Brute force (No Partitioning) send_local message implemented in FLAMEGPU_Kernels */

/** add_send_local_message
 * Function for all types of message partitioning
 * Adds a new send_local agent to the xmachine_memory_send_local_list list using a linear mapping
 * @param agents	xmachine_memory_send_local_list agent list
 * @param from_id	message variable of type int
 * @param value	message variable of type float
 */
 
 __FLAME_GPU_FUNC__ void add_send_local_message(xmachine_message_send_local_list* send_local_messages, int from_id, float value);
 
/** get_first_send_local_message
 * Get first message function for non partitioned (brute force) messages
 * @param send_local_messages message list
 * @return        returns the first message from the message list (offset depending on agent block)
 */
__FLAME_GPU_FUNC__ xmachine_message_send_local * get_first_send_local_message(xmachine_message_send_local_list* send_local_messages);

/** get_next_send_local_message
 * Get first message function for non partitioned (brute force) messages
 * @param current the current message struct
 * @param send_local_messages message list
 * @return        returns the first message from the message list (offset depending on agent block)
 */
__FLAME_GPU_FUNC__ xmachine_message_send_local * get_next_send_local_message(xmachine_message_send_local* current, xmachine_message_send_local_list* send_local_messages);

  
/* Agent Function Prototypes implemented in FLAMEGPU_Kernels */

/** add_vertice_agent
 * Adds a new continuous valued vertice agent to the xmachine_memory_vertice_list list using a linear mapping. Note that any agent variables with an arrayLength are ommited and not support during the creation of new agents on the fly.
 * @param agents xmachine_memory_vertice_list agent list
 * @param id	agent agent variable of type int
 * @param value	agent agent variable of type float
 * @param add_value	agent agent variable of type float
 * @param previous	agent agent variable of type float
 * @param max_lag	agent agent variable of type int
 * @param current_lag	agent agent variable of type int
 * @param min	agent agent variable of type float
 * @param max	agent agent variable of type float
 * @param need_test	agent agent variable of type int
 * @param correct	agent agent variable of type int
 */
__FLAME_GPU_FUNC__ void add_vertice_agent(xmachine_memory_vertice_list* agents, int id, float value, float add_value, float previous, int max_lag, int current_lag, float min, float max, int need_test, int correct);

/** get_vertice_agent_array_value
 *  Template function for accessing vertice agent array memory variables.
 *  @param array Agent memory array
 *  @param index to lookup
 *  @return return value
 */
template<typename T>
__FLAME_GPU_FUNC__ T get_vertice_agent_array_value(T *array, unsigned int index);

/** set_vertice_agent_array_value
 *  Template function for setting vertice agent array memory variables.
 *  @param array Agent memory array
 *  @param index to lookup
 *  @param return value
 */
template<typename T>
__FLAME_GPU_FUNC__ void set_vertice_agent_array_value(T *array, unsigned int index, T value);


  


/* Agent ID Generation functions implemented in simulation.cu and FLAMEGPU_kernals.cu*/

extern int h_current_value_generate_vertice_id;
__device__ int d_current_value_generate_vertice_id;
__FLAME_GPU_HOST_FUNC__ __FLAME_GPU_FUNC__ int generate_vertice_id();
void set_initial_vertice_id(int firstID);


/* Graph loading function prototypes implemented in io.cu */


  
/* Simulation function prototypes implemented in simulation.cu */
/** getIterationNumber
 *  Get the iteration number (host)
 */
extern unsigned int getIterationNumber();

/** initialise
 * Initialise the simulation. Allocated host and device memory. Reads the initial agent configuration from XML.
 * @param input        XML file path for agent initial configuration
 */
extern void initialise(char * input);

/** cleanup
 * Function cleans up any memory allocations on the host and device
 */
extern void cleanup();

/** singleIteration
 *	Performs a single iteration of the simulation. I.e. performs each agent function on each function layer in the correct order.
 */
extern void singleIteration();

/** saveIterationData
 * Reads the current agent data fromt he device and saves it to XML
 * @param	outputpath	file path to XML file used for output of agent data
 * @param	iteration_number
 * @param h_vertices Pointer to agent list on the host
 * @param d_vertices Pointer to agent list on the GPU device
 * @param h_xmachine_memory_vertice_count Pointer to agent counter
 */
extern void saveIterationData(char* outputpath, int iteration_number, xmachine_memory_vertice_list* h_vertices_default, xmachine_memory_vertice_list* d_vertices_default, int h_xmachine_memory_vertice_default_count);


/** readInitialStates
 * Reads the current agent data from the device and saves it to XML
 * @param	inputpath	file path to XML file used for input of agent data
 * @param h_vertices Pointer to agent list on the host
 * @param h_xmachine_memory_vertice_count Pointer to agent counter
 */
extern void readInitialStates(char* inputpath, xmachine_memory_vertice_list* h_vertices, int* h_xmachine_memory_vertice_count);

/** set_exit_early
 * exits the simulation on the step this is called
 */
extern void set_exit_early();

/** get_exit_early
 * gets whether the simulation is ending this simulation step
 */
extern bool get_exit_early();




/* Return functions used by external code to get agent data from device */

    
/** get_agent_vertice_MAX_count
 * Gets the max agent count for the vertice agent type 
 * @return		the maximum vertice agent count
 */
extern int get_agent_vertice_MAX_count();



/** get_agent_vertice_default_count
 * Gets the agent count for the vertice agent type in state default
 * @return		the current vertice agent count in state default
 */
extern int get_agent_vertice_default_count();

/** reset_default_count
 * Resets the agent count of the vertice in state default to 0. This is useful for interacting with some visualisations.
 */
extern void reset_vertice_default_count();

/** get_device_vertice_default_agents
 * Gets a pointer to xmachine_memory_vertice_list on the GPU device
 * @return		a xmachine_memory_vertice_list on the GPU device
 */
extern xmachine_memory_vertice_list* get_device_vertice_default_agents();

/** get_host_vertice_default_agents
 * Gets a pointer to xmachine_memory_vertice_list on the CPU host
 * @return		a xmachine_memory_vertice_list on the CPU host
 */
extern xmachine_memory_vertice_list* get_host_vertice_default_agents();


/** sort_vertices_default
 * Sorts an agent state list by providing a CUDA kernal to generate key value pairs
 * @param		a pointer CUDA kernal function to generate key value pairs
 */
void sort_vertices_default(void (*generate_key_value_pairs)(unsigned int* keys, unsigned int* values, xmachine_memory_vertice_list* agents));



/* Host based access of agent variables*/

/** int get_vertice_default_variable_id(unsigned int index)
 * Gets the value of the id variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable id
 */
__host__ int get_vertice_default_variable_id(unsigned int index);

/** float get_vertice_default_variable_value(unsigned int index)
 * Gets the value of the value variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable value
 */
__host__ float get_vertice_default_variable_value(unsigned int index);

/** float get_vertice_default_variable_add_value(unsigned int index)
 * Gets the value of the add_value variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable add_value
 */
__host__ float get_vertice_default_variable_add_value(unsigned int index);

/** float get_vertice_default_variable_previous(unsigned int index)
 * Gets the value of the previous variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable previous
 */
__host__ float get_vertice_default_variable_previous(unsigned int index);

/** int get_vertice_default_variable_max_lag(unsigned int index)
 * Gets the value of the max_lag variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable max_lag
 */
__host__ int get_vertice_default_variable_max_lag(unsigned int index);

/** int get_vertice_default_variable_current_lag(unsigned int index)
 * Gets the value of the current_lag variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable current_lag
 */
__host__ int get_vertice_default_variable_current_lag(unsigned int index);

/** float get_vertice_default_variable_edges(unsigned int index, unsigned int element)
 * Gets the element-th value of the edges variable array of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @param element the element index within the variable array
 * @return element-th value of agent variable edges
 */
__host__ float get_vertice_default_variable_edges(unsigned int index, unsigned int element);

/** float get_vertice_default_variable_min(unsigned int index)
 * Gets the value of the min variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable min
 */
__host__ float get_vertice_default_variable_min(unsigned int index);

/** float get_vertice_default_variable_max(unsigned int index)
 * Gets the value of the max variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable max
 */
__host__ float get_vertice_default_variable_max(unsigned int index);

/** int get_vertice_default_variable_need_test(unsigned int index)
 * Gets the value of the need_test variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable need_test
 */
__host__ int get_vertice_default_variable_need_test(unsigned int index);

/** int get_vertice_default_variable_correct(unsigned int index)
 * Gets the value of the correct variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable correct
 */
__host__ int get_vertice_default_variable_correct(unsigned int index);




/* Host based agent creation functions */

/** h_allocate_agent_vertice
 * Utility function to allocate and initialise an agent struct on the host.
 * @return address of a host-allocated vertice struct.
 */
xmachine_memory_vertice* h_allocate_agent_vertice();
/** h_free_agent_vertice
 * Utility function to free a host-allocated agent struct.
 * This also deallocates any agent variable arrays, and sets the pointer to null
 * @param agent address of pointer to the host allocated struct
 */
void h_free_agent_vertice(xmachine_memory_vertice** agent);
/** h_allocate_agent_vertice_array
 * Utility function to allocate an array of structs for  vertice agents.
 * @param count the number of structs to allocate memory for.
 * @return pointer to the allocated array of structs
 */
xmachine_memory_vertice** h_allocate_agent_vertice_array(unsigned int count);
/** h_free_agent_vertice_array(
 * Utility function to deallocate a host array of agent structs, including agent variables, and set pointer values to NULL.
 * @param agents the address of the pointer to the host array of structs.
 * @param count the number of elements in the AoS, to deallocate individual elements.
 */
void h_free_agent_vertice_array(xmachine_memory_vertice*** agents, unsigned int count);


/** h_add_agent_vertice_default
 * Host function to add a single agent of type vertice to the default state on the device.
 * This invokes many cudaMempcy, and an append kernel launch. 
 * If multiple agents are to be created in a single iteration, consider h_add_agent_vertice_default instead.
 * @param agent pointer to agent struct on the host. Agent member arrays are supported.
 */
void h_add_agent_vertice_default(xmachine_memory_vertice* agent);

/** h_add_agents_vertice_default(
 * Host function to add multiple agents of type vertice to the default state on the device if possible.
 * This includes the transparent conversion from AoS to SoA, many calls to cudaMemcpy and an append kernel.
 * @param agents pointer to host struct of arrays of vertice agents
 * @param count the number of agents to copy from the host to the device.
 */
void h_add_agents_vertice_default(xmachine_memory_vertice** agents, unsigned int count);

  
  
/* Analytics functions for each varible in each state*/
typedef enum {
  REDUCTION_MAX,
  REDUCTION_MIN,
  REDUCTION_SUM
}reduction_operator;


/** int reduce_vertice_default_id_variable();
 * Reduction functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the reduced variable value of the specified agent name and state
 */
int reduce_vertice_default_id_variable();



/** int count_vertice_default_id_variable(int count_value){
 * Count can be used for integer only agent variables and allows unique values to be counted using a reduction. Useful for generating histograms.
 * @param count_value The unique value which should be counted
 * @return The number of unique values of the count_value found in the agent state variable list
 */
int count_vertice_default_id_variable(int count_value);

/** int min_vertice_default_id_variable();
 * Min functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
int min_vertice_default_id_variable();
/** int max_vertice_default_id_variable();
 * Max functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
int max_vertice_default_id_variable();

/** float reduce_vertice_default_value_variable();
 * Reduction functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the reduced variable value of the specified agent name and state
 */
float reduce_vertice_default_value_variable();



/** float min_vertice_default_value_variable();
 * Min functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
float min_vertice_default_value_variable();
/** float max_vertice_default_value_variable();
 * Max functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
float max_vertice_default_value_variable();

/** float reduce_vertice_default_add_value_variable();
 * Reduction functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the reduced variable value of the specified agent name and state
 */
float reduce_vertice_default_add_value_variable();



/** float min_vertice_default_add_value_variable();
 * Min functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
float min_vertice_default_add_value_variable();
/** float max_vertice_default_add_value_variable();
 * Max functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
float max_vertice_default_add_value_variable();

/** float reduce_vertice_default_previous_variable();
 * Reduction functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the reduced variable value of the specified agent name and state
 */
float reduce_vertice_default_previous_variable();



/** float min_vertice_default_previous_variable();
 * Min functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
float min_vertice_default_previous_variable();
/** float max_vertice_default_previous_variable();
 * Max functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
float max_vertice_default_previous_variable();

/** int reduce_vertice_default_max_lag_variable();
 * Reduction functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the reduced variable value of the specified agent name and state
 */
int reduce_vertice_default_max_lag_variable();



/** int count_vertice_default_max_lag_variable(int count_value){
 * Count can be used for integer only agent variables and allows unique values to be counted using a reduction. Useful for generating histograms.
 * @param count_value The unique value which should be counted
 * @return The number of unique values of the count_value found in the agent state variable list
 */
int count_vertice_default_max_lag_variable(int count_value);

/** int min_vertice_default_max_lag_variable();
 * Min functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
int min_vertice_default_max_lag_variable();
/** int max_vertice_default_max_lag_variable();
 * Max functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
int max_vertice_default_max_lag_variable();

/** int reduce_vertice_default_current_lag_variable();
 * Reduction functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the reduced variable value of the specified agent name and state
 */
int reduce_vertice_default_current_lag_variable();



/** int count_vertice_default_current_lag_variable(int count_value){
 * Count can be used for integer only agent variables and allows unique values to be counted using a reduction. Useful for generating histograms.
 * @param count_value The unique value which should be counted
 * @return The number of unique values of the count_value found in the agent state variable list
 */
int count_vertice_default_current_lag_variable(int count_value);

/** int min_vertice_default_current_lag_variable();
 * Min functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
int min_vertice_default_current_lag_variable();
/** int max_vertice_default_current_lag_variable();
 * Max functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
int max_vertice_default_current_lag_variable();

/** float reduce_vertice_default_min_variable();
 * Reduction functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the reduced variable value of the specified agent name and state
 */
float reduce_vertice_default_min_variable();



/** float min_vertice_default_min_variable();
 * Min functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
float min_vertice_default_min_variable();
/** float max_vertice_default_min_variable();
 * Max functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
float max_vertice_default_min_variable();

/** float reduce_vertice_default_max_variable();
 * Reduction functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the reduced variable value of the specified agent name and state
 */
float reduce_vertice_default_max_variable();



/** float min_vertice_default_max_variable();
 * Min functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
float min_vertice_default_max_variable();
/** float max_vertice_default_max_variable();
 * Max functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
float max_vertice_default_max_variable();

/** int reduce_vertice_default_need_test_variable();
 * Reduction functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the reduced variable value of the specified agent name and state
 */
int reduce_vertice_default_need_test_variable();



/** int count_vertice_default_need_test_variable(int count_value){
 * Count can be used for integer only agent variables and allows unique values to be counted using a reduction. Useful for generating histograms.
 * @param count_value The unique value which should be counted
 * @return The number of unique values of the count_value found in the agent state variable list
 */
int count_vertice_default_need_test_variable(int count_value);

/** int min_vertice_default_need_test_variable();
 * Min functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
int min_vertice_default_need_test_variable();
/** int max_vertice_default_need_test_variable();
 * Max functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
int max_vertice_default_need_test_variable();

/** int reduce_vertice_default_correct_variable();
 * Reduction functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the reduced variable value of the specified agent name and state
 */
int reduce_vertice_default_correct_variable();



/** int count_vertice_default_correct_variable(int count_value){
 * Count can be used for integer only agent variables and allows unique values to be counted using a reduction. Useful for generating histograms.
 * @param count_value The unique value which should be counted
 * @return The number of unique values of the count_value found in the agent state variable list
 */
int count_vertice_default_correct_variable(int count_value);

/** int min_vertice_default_correct_variable();
 * Min functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
int min_vertice_default_correct_variable();
/** int max_vertice_default_correct_variable();
 * Max functions can be used by visualisations, step and exit functions to gather data for plotting or updating global variables
 * @return the minimum variable value of the specified agent name and state
 */
int max_vertice_default_correct_variable();


  
/* global constant variables */

__constant__ int VERTICES_COUNT;

/** set_VERTICES_COUNT
 * Sets the constant variable VERTICES_COUNT on the device which can then be used in the agent functions.
 * @param h_VERTICES_COUNT value to set the variable
 */
extern void set_VERTICES_COUNT(int* h_VERTICES_COUNT);

extern const int* get_VERTICES_COUNT();


extern int h_env_VERTICES_COUNT;


/** getMaximumBound
 * Returns the maximum agent positions determined from the initial loading of agents
 * @return 	a three component float indicating the maximum x, y and z positions of all agents
 */
glm::vec3 getMaximumBounds();

/** getMinimumBounds
 * Returns the minimum agent positions determined from the initial loading of agents
 * @return 	a three component float indicating the minimum x, y and z positions of all agents
 */
glm::vec3 getMinimumBounds();
    
    
#ifdef VISUALISATION
/** initVisualisation
 * Prototype for method which initialises the visualisation. Must be implemented in separate file
 * @param argc	the argument count from the main function used with GLUT
 * @param argv	the argument values from the main function used with GLUT
 */
extern void initVisualisation();

extern void runVisualisation();


#endif

#if defined(PROFILE)
#include "nvToolsExt.h"

#define PROFILE_WHITE   0x00eeeeee
#define PROFILE_GREEN   0x0000ff00
#define PROFILE_BLUE    0x000000ff
#define PROFILE_YELLOW  0x00ffff00
#define PROFILE_MAGENTA 0x00ff00ff
#define PROFILE_CYAN    0x0000ffff
#define PROFILE_RED     0x00ff0000
#define PROFILE_GREY    0x00999999
#define PROFILE_LILAC   0xC8A2C8

const uint32_t profile_colors[] = {
  PROFILE_WHITE,
  PROFILE_GREEN,
  PROFILE_BLUE,
  PROFILE_YELLOW,
  PROFILE_MAGENTA,
  PROFILE_CYAN,
  PROFILE_RED,
  PROFILE_GREY,
  PROFILE_LILAC
};
const int num_profile_colors = sizeof(profile_colors) / sizeof(uint32_t);

// Externed value containing colour information.
extern unsigned int g_profile_colour_id;

#define PROFILE_PUSH_RANGE(name) { \
    unsigned int color_id = g_profile_colour_id % num_profile_colors;\
    nvtxEventAttributes_t eventAttrib = {0}; \
    eventAttrib.version = NVTX_VERSION; \
    eventAttrib.size = NVTX_EVENT_ATTRIB_STRUCT_SIZE; \
    eventAttrib.colorType = NVTX_COLOR_ARGB; \
    eventAttrib.color = profile_colors[color_id]; \
    eventAttrib.messageType = NVTX_MESSAGE_TYPE_ASCII; \
    eventAttrib.message.ascii = name; \
    nvtxRangePushEx(&eventAttrib); \
    g_profile_colour_id++; \
}
#define PROFILE_POP_RANGE() nvtxRangePop();

// Class for simple fire-and-forget profile ranges (ie. functions with multiple return conditions.)
class ProfileScopedRange {
public:
    ProfileScopedRange(const char * name){
      PROFILE_PUSH_RANGE(name);
    }
    ~ProfileScopedRange(){
      PROFILE_POP_RANGE();
    }
};
#define PROFILE_SCOPED_RANGE(name) ProfileScopedRange uniq_name_using_macros(name);
#else
#define PROFILE_PUSH_RANGE(name)
#define PROFILE_POP_RANGE()
#define PROFILE_SCOPED_RANGE(name)
#endif


#endif //__HEADER

