
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


#ifndef _FLAMEGPU_KERNELS_H_
#define _FLAMEGPU_KERNELS_H_

#include "header.h"


/* Agent count constants */

__constant__ int d_xmachine_memory_vertice_count;

/* Agent state count constants */

__constant__ int d_xmachine_memory_vertice_default_count;


/* Message constants */

/* send_local Message variables */
/* Non partitioned, spatial partitioned and on-graph partitioned message variables  */
__constant__ int d_message_send_local_count;         /**< message list counter*/
__constant__ int d_message_send_local_output_type;   /**< message output type (single or optional)*/

	

/* Graph Constants */


/* Graph device array pointer(s) */


/* Graph host array pointer(s) */

    
//include each function file

#include "functions.c"
    
/* Texture bindings */

    
#define WRAP(x,m) (((x)<m)?(x):(x%m)) /**< Simple wrap */
#define sWRAP(x,m) (((x)<m)?(((x)<0)?(m+(x)):(x)):(m-(x))) /**<signed integer wrap (no modulus) for negatives where 2m > |x| > m */

//PADDING WILL ONLY AVOID SM CONFLICTS FOR 32BIT
//SM_OFFSET REQUIRED AS FERMI STARTS INDEXING MEMORY FROM LOCATION 0 (i.e. NULL)??
__constant__ int d_SM_START;
__constant__ int d_PADDING;

//SM addressing macro to avoid conflicts (32 bit only)
#define SHARE_INDEX(i, s) ((((s) + d_PADDING)* (i))+d_SM_START) /**<offset struct size by padding to avoid bank conflicts */

//if doubel support is needed then define the following function which requires sm_13 or later
#ifdef _DOUBLE_SUPPORT_REQUIRED_
__inline__ __device__ double tex1DfetchDouble(texture<int2, 1, cudaReadModeElementType> tex, int i)
{
	int2 v = tex1Dfetch(tex, i);
  //IF YOU HAVE AN ERROR HERE THEN YOU ARE USING DOUBLE VALUES IN AGENT MEMORY AND NOT COMPILING FOR DOUBLE SUPPORTED HARDWARE
  //To compile for double supported hardware change the CUDA Build rule property "Use sm_13 Architecture (double support)" on the CUDA-Specific Propert Page of the CUDA Build Rule for simulation.cu
	return __hiloint2double(v.y, v.x);
}
#endif

/* Helper functions */
/** next_cell
 * Function used for finding the next cell when using spatial partitioning
 * Upddates the relative cell variable which can have value of -1, 0 or +1
 * @param relative_cell pointer to the relative cell position
 * @return boolean if there is a next cell. True unless relative_Cell value was 1,1,1
 */
__device__ bool next_cell3D(glm::ivec3* relative_cell)
{
	if (relative_cell->x < 1)
	{
		relative_cell->x++;
		return true;
	}
	relative_cell->x = -1;

	if (relative_cell->y < 1)
	{
		relative_cell->y++;
		return true;
	}
	relative_cell->y = -1;
	
	if (relative_cell->z < 1)
	{
		relative_cell->z++;
		return true;
	}
	relative_cell->z = -1;
	
	return false;
}

/** next_cell2D
 * Function used for finding the next cell when using spatial partitioning. Z component is ignored
 * Upddates the relative cell variable which can have value of -1, 0 or +1
 * @param relative_cell pointer to the relative cell position
 * @return boolean if there is a next cell. True unless relative_Cell value was 1,1
 */
__device__ bool next_cell2D(glm::ivec3* relative_cell)
{
	if (relative_cell->x < 1)
	{
		relative_cell->x++;
		return true;
	}
	relative_cell->x = -1;

	if (relative_cell->y < 1)
	{
		relative_cell->y++;
		return true;
	}
	relative_cell->y = -1;
	
	return false;
}


////////////////////////////////////////////////////////////////////////////////////////////////////////
/* Dynamically created vertice agent functions */

/** reset_vertice_scan_input
 * vertice agent reset scan input function
 * @param agents The xmachine_memory_vertice_list agent list
 */
__global__ void reset_vertice_scan_input(xmachine_memory_vertice_list* agents){

	//global thread index
	int index = (blockIdx.x*blockDim.x) + threadIdx.x;

	agents->_position[index] = 0;
	agents->_scan_input[index] = 0;
}



/** scatter_vertice_Agents
 * vertice scatter agents function (used after agent birth/death)
 * @param agents_dst xmachine_memory_vertice_list agent list destination
 * @param agents_src xmachine_memory_vertice_list agent list source
 * @param dst_agent_count index to start scattering agents from
 */
__global__ void scatter_vertice_Agents(xmachine_memory_vertice_list* agents_dst, xmachine_memory_vertice_list* agents_src, int dst_agent_count, int number_to_scatter){
	//global thread index
	int index = (blockIdx.x*blockDim.x) + threadIdx.x;

	int _scan_input = agents_src->_scan_input[index];

	//if optional message is to be written. 
	//must check agent is within number to scatter as unused threads may have scan input = 1
	if ((_scan_input == 1)&&(index < number_to_scatter)){
		int output_index = agents_src->_position[index] + dst_agent_count;

		//AoS - xmachine_message_location Un-Coalesced scattered memory write     
        agents_dst->_position[output_index] = output_index;        
		agents_dst->id[output_index] = agents_src->id[index];        
		agents_dst->value[output_index] = agents_src->value[index];        
		agents_dst->add_value[output_index] = agents_src->add_value[index];        
		agents_dst->previous[output_index] = agents_src->previous[index];        
		agents_dst->max_lag[output_index] = agents_src->max_lag[index];        
		agents_dst->current_lag[output_index] = agents_src->current_lag[index];
	    for (int i=0; i<17; i++){
	      agents_dst->edges[(i*xmachine_memory_vertice_MAX)+output_index] = agents_src->edges[(i*xmachine_memory_vertice_MAX)+index];
	    }        
		agents_dst->min[output_index] = agents_src->min[index];        
		agents_dst->max[output_index] = agents_src->max[index];        
		agents_dst->need_test[output_index] = agents_src->need_test[index];        
		agents_dst->correct[output_index] = agents_src->correct[index];
	}
}

/** append_vertice_Agents
 * vertice scatter agents function (used after agent birth/death)
 * @param agents_dst xmachine_memory_vertice_list agent list destination
 * @param agents_src xmachine_memory_vertice_list agent list source
 * @param dst_agent_count index to start scattering agents from
 */
__global__ void append_vertice_Agents(xmachine_memory_vertice_list* agents_dst, xmachine_memory_vertice_list* agents_src, int dst_agent_count, int number_to_append){
	//global thread index
	int index = (blockIdx.x*blockDim.x) + threadIdx.x;

	//must check agent is within number to append as unused threads may have scan input = 1
    if (index < number_to_append){
	    int output_index = index + dst_agent_count;

	    //AoS - xmachine_message_location Un-Coalesced scattered memory write
	    agents_dst->_position[output_index] = output_index;
	    agents_dst->id[output_index] = agents_src->id[index];
	    agents_dst->value[output_index] = agents_src->value[index];
	    agents_dst->add_value[output_index] = agents_src->add_value[index];
	    agents_dst->previous[output_index] = agents_src->previous[index];
	    agents_dst->max_lag[output_index] = agents_src->max_lag[index];
	    agents_dst->current_lag[output_index] = agents_src->current_lag[index];
	    for (int i=0; i<17; i++){
	      agents_dst->edges[(i*xmachine_memory_vertice_MAX)+output_index] = agents_src->edges[(i*xmachine_memory_vertice_MAX)+index];
	    }
	    agents_dst->min[output_index] = agents_src->min[index];
	    agents_dst->max[output_index] = agents_src->max[index];
	    agents_dst->need_test[output_index] = agents_src->need_test[index];
	    agents_dst->correct[output_index] = agents_src->correct[index];
    }
}

/** add_vertice_agent
 * Continuous vertice agent add agent function writes agent data to agent swap
 * @param agents xmachine_memory_vertice_list to add agents to 
 * @param id agent variable of type int
 * @param value agent variable of type float
 * @param add_value agent variable of type float
 * @param previous agent variable of type float
 * @param max_lag agent variable of type int
 * @param current_lag agent variable of type int
 * @param edges agent variable of type float
 * @param min agent variable of type float
 * @param max agent variable of type float
 * @param need_test agent variable of type int
 * @param correct agent variable of type int
 */
template <int AGENT_TYPE>
__device__ void add_vertice_agent(xmachine_memory_vertice_list* agents, int id, float value, float add_value, float previous, int max_lag, int current_lag, float min, float max, int need_test, int correct){
	
	int index;
    
    //calculate the agents index in global agent list (depends on agent type)
	if (AGENT_TYPE == DISCRETE_2D){
		int width = (blockDim.x* gridDim.x);
		glm::ivec2 global_position;
		global_position.x = (blockIdx.x*blockDim.x) + threadIdx.x;
		global_position.y = (blockIdx.y*blockDim.y) + threadIdx.y;
		index = global_position.x + (global_position.y* width);
	}else//AGENT_TYPE == CONTINOUS
		index = threadIdx.x + blockIdx.x*blockDim.x;

	//for prefix sum
	agents->_position[index] = 0;
	agents->_scan_input[index] = 1;

	//write data to new buffer
	agents->id[index] = id;
	agents->value[index] = value;
	agents->add_value[index] = add_value;
	agents->previous[index] = previous;
	agents->max_lag[index] = max_lag;
	agents->current_lag[index] = current_lag;
	agents->min[index] = min;
	agents->max[index] = max;
	agents->need_test[index] = need_test;
	agents->correct[index] = correct;

}

//non templated version assumes DISCRETE_2D but works also for CONTINUOUS
__device__ void add_vertice_agent(xmachine_memory_vertice_list* agents, int id, float value, float add_value, float previous, int max_lag, int current_lag, float min, float max, int need_test, int correct){
    add_vertice_agent<DISCRETE_2D>(agents, id, value, add_value, previous, max_lag, current_lag, min, max, need_test, correct);
}

/** reorder_vertice_agents
 * Continuous vertice agent areorder function used after key value pairs have been sorted
 * @param values sorted index values
 * @param unordered_agents list of unordered agents
 * @ param ordered_agents list used to output ordered agents
 */
__global__ void reorder_vertice_agents(unsigned int* values, xmachine_memory_vertice_list* unordered_agents, xmachine_memory_vertice_list* ordered_agents)
{
	int index = (blockIdx.x*blockDim.x) + threadIdx.x;

	uint old_pos = values[index];

	//reorder agent data
	ordered_agents->id[index] = unordered_agents->id[old_pos];
	ordered_agents->value[index] = unordered_agents->value[old_pos];
	ordered_agents->add_value[index] = unordered_agents->add_value[old_pos];
	ordered_agents->previous[index] = unordered_agents->previous[old_pos];
	ordered_agents->max_lag[index] = unordered_agents->max_lag[old_pos];
	ordered_agents->current_lag[index] = unordered_agents->current_lag[old_pos];
	for (int i=0; i<17; i++){
	  ordered_agents->edges[(i*xmachine_memory_vertice_MAX)+index] = unordered_agents->edges[(i*xmachine_memory_vertice_MAX)+old_pos];
	}
	ordered_agents->min[index] = unordered_agents->min[old_pos];
	ordered_agents->max[index] = unordered_agents->max[old_pos];
	ordered_agents->need_test[index] = unordered_agents->need_test[old_pos];
	ordered_agents->correct[index] = unordered_agents->correct[old_pos];
}

/** get_vertice_agent_array_value
 *  Template function for accessing vertice agent array memory variables. Assumes array points to the first element of the agents array values (offset by agent index)
 *  @param array Agent memory array
 *  @param index to lookup
 *  @return return value
 */
template<typename T>
__FLAME_GPU_FUNC__ T get_vertice_agent_array_value(T *array, uint index){
	// Null check for out of bounds agents (brute force communication. )
	if(array != nullptr){
	    return array[index*xmachine_memory_vertice_MAX];
    } else {
    	// Return the default value for this data type 
	    return 0;
    }
}

/** set_vertice_agent_array_value
 *  Template function for setting vertice agent array memory variables. Assumes array points to the first element of the agents array values (offset by agent index)
 *  @param array Agent memory array
 *  @param index to lookup
 *  @param return value
 */
template<typename T>
__FLAME_GPU_FUNC__ void set_vertice_agent_array_value(T *array, uint index, T value){
	// Null check for out of bounds agents (brute force communication. )
	if(array != nullptr){
	    array[index*xmachine_memory_vertice_MAX] = value;
    }
}

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/* Dynamically created send_local message functions */


/** add_send_local_message
 * Add non partitioned or spatially partitioned send_local message
 * @param messages xmachine_message_send_local_list message list to add too
 * @param from_id agent variable of type int
 * @param value agent variable of type float
 */
__device__ void add_send_local_message(xmachine_message_send_local_list* messages, int from_id, float value){

	//global thread index
	int index = (blockIdx.x*blockDim.x) + threadIdx.x + d_message_send_local_count;

	int _position;
	int _scan_input;

	//decide output position
	if(d_message_send_local_output_type == single_message){
		_position = index; //same as agent position
		_scan_input = 0;
	}else if (d_message_send_local_output_type == optional_message){
		_position = 0;	   //to be calculated using Prefix sum
		_scan_input = 1;
	}

	//AoS - xmachine_message_send_local Coalesced memory write
	messages->_scan_input[index] = _scan_input;	
	messages->_position[index] = _position;
	messages->from_id[index] = from_id;
	messages->value[index] = value;

}

/**
 * Scatter non partitioned or spatially partitioned send_local message (for optional messages)
 * @param messages scatter_optional_send_local_messages Sparse xmachine_message_send_local_list message list
 * @param message_swap temp xmachine_message_send_local_list message list to scatter sparse messages to
 */
__global__ void scatter_optional_send_local_messages(xmachine_message_send_local_list* messages, xmachine_message_send_local_list* messages_swap){
	//global thread index
	int index = (blockIdx.x*blockDim.x) + threadIdx.x;

	int _scan_input = messages_swap->_scan_input[index];

	//if optional message is to be written
	if (_scan_input == 1){
		int output_index = messages_swap->_position[index] + d_message_send_local_count;

		//AoS - xmachine_message_send_local Un-Coalesced scattered memory write
		messages->_position[output_index] = output_index;
		messages->from_id[output_index] = messages_swap->from_id[index];
		messages->value[output_index] = messages_swap->value[index];				
	}
}

/** reset_send_local_swaps
 * Reset non partitioned or spatially partitioned send_local message swaps (for scattering optional messages)
 * @param message_swap message list to reset _position and _scan_input values back to 0
 */
__global__ void reset_send_local_swaps(xmachine_message_send_local_list* messages_swap){

	//global thread index
	int index = (blockIdx.x*blockDim.x) + threadIdx.x;

	messages_swap->_position[index] = 0;
	messages_swap->_scan_input[index] = 0;
}

/* Message functions */

__device__ xmachine_message_send_local* get_first_send_local_message(xmachine_message_send_local_list* messages){

	extern __shared__ int sm_data [];
	char* message_share = (char*)&sm_data[0];
	
	//wrap size is the number of tiles required to load all messages
	int wrap_size = (ceil((float)d_message_send_local_count/ blockDim.x)* blockDim.x);

	//if no messages then return a null pointer (false)
	if (wrap_size == 0)
		return nullptr;

	//global thread index
	int global_index = (blockIdx.x*blockDim.x) + threadIdx.x;

	//global thread index
	int index = WRAP(global_index, wrap_size);

	//SoA to AoS - xmachine_message_send_local Coalesced memory read
	xmachine_message_send_local temp_message;
	temp_message._position = messages->_position[index];
	temp_message.from_id = messages->from_id[index];
	temp_message.value = messages->value[index];

	//AoS to shared memory
	int message_index = SHARE_INDEX(threadIdx.y*blockDim.x+threadIdx.x, sizeof(xmachine_message_send_local));
	xmachine_message_send_local* sm_message = ((xmachine_message_send_local*)&message_share[message_index]);
	sm_message[0] = temp_message;

	__syncthreads();

  //HACK FOR 64 bit addressing issue in sm
	return ((xmachine_message_send_local*)&message_share[d_SM_START]);
}

__device__ xmachine_message_send_local* get_next_send_local_message(xmachine_message_send_local* message, xmachine_message_send_local_list* messages){

	extern __shared__ int sm_data [];
	char* message_share = (char*)&sm_data[0];
	
	//wrap size is the number of tiles required to load all messages
	int wrap_size = ceil((float)d_message_send_local_count/ blockDim.x)*blockDim.x;

	int i = WRAP((message->_position + 1),wrap_size);

	//If end of messages (last message not multiple of gridsize) go to 0 index
	if (i >= d_message_send_local_count)
		i = 0;

	//Check if back to start position of first message
	if (i == WRAP((blockDim.x* blockIdx.x), wrap_size))
		return nullptr;

	int tile = floor((float)i/(blockDim.x)); //tile is round down position over blockDim
	i = i % blockDim.x;						 //mod i for shared memory index

	//if count == Block Size load next tile int shared memory values
	if (i == 0){
		__syncthreads();					//make sure we don't change shared memory until all threads are here (important for emu-debug mode)
		
		//SoA to AoS - xmachine_message_send_local Coalesced memory read
		int index = (tile* blockDim.x) + threadIdx.x;
		xmachine_message_send_local temp_message;
		temp_message._position = messages->_position[index];
		temp_message.from_id = messages->from_id[index];
		temp_message.value = messages->value[index];

		//AoS to shared memory
		int message_index = SHARE_INDEX(threadIdx.y*blockDim.x+threadIdx.x, sizeof(xmachine_message_send_local));
		xmachine_message_send_local* sm_message = ((xmachine_message_send_local*)&message_share[message_index]);
		sm_message[0] = temp_message;

		__syncthreads();					//make sure we don't start returning messages until all threads have updated shared memory
	}

	int message_index = SHARE_INDEX(i, sizeof(xmachine_message_send_local));
	return ((xmachine_message_send_local*)&message_share[message_index]);
}

	
/////////////////////////////////////////////////////////////////////////////////////////////////////////
/* Dynamically created GPU kernels  */



/**
 *
 */
__global__ void GPUFLAME_send_message(xmachine_memory_vertice_list* agents, xmachine_message_send_local_list* send_local_messages, RNG_rand48* rand48){
	
	//continuous agent: index is agent position in 1D agent list
	int index = (blockIdx.x * blockDim.x) + threadIdx.x;
  
    //For agents not using non partitioned message input check the agent bounds
    if (index >= d_xmachine_memory_vertice_count)
        return;
    

	//SoA to AoS - xmachine_memory_send_message Coalesced memory read (arrays point to first item for agent index)
	xmachine_memory_vertice agent;
    
    // Thread bounds already checked, but the agent function will still execute. load default values?
	
	agent.id = agents->id[index];
	agent.value = agents->value[index];
	agent.add_value = agents->add_value[index];
	agent.previous = agents->previous[index];
	agent.max_lag = agents->max_lag[index];
	agent.current_lag = agents->current_lag[index];
    agent.edges = &(agents->edges[index]);
	agent.min = agents->min[index];
	agent.max = agents->max[index];
	agent.need_test = agents->need_test[index];
	agent.correct = agents->correct[index];

	//FLAME function call
	int dead = !send_message(&agent, send_local_messages	, rand48);
	

	//continuous agent: set reallocation flag
	agents->_scan_input[index]  = dead; 

	//AoS to SoA - xmachine_memory_send_message Coalesced memory write (ignore arrays)
	agents->id[index] = agent.id;
	agents->value[index] = agent.value;
	agents->add_value[index] = agent.add_value;
	agents->previous[index] = agent.previous;
	agents->max_lag[index] = agent.max_lag;
	agents->current_lag[index] = agent.current_lag;
	agents->min[index] = agent.min;
	agents->max[index] = agent.max;
	agents->need_test[index] = agent.need_test;
	agents->correct[index] = agent.correct;
}

/**
 *
 */
__global__ void GPUFLAME_read_message(xmachine_memory_vertice_list* agents, xmachine_message_send_local_list* send_local_messages, RNG_rand48* rand48){
	
	//continuous agent: index is agent position in 1D agent list
	int index = (blockIdx.x * blockDim.x) + threadIdx.x;
  
    
    //No partitioned input requires threads to be launched beyond the agent count to ensure full block sizes
    

	//SoA to AoS - xmachine_memory_read_message Coalesced memory read (arrays point to first item for agent index)
	xmachine_memory_vertice agent;
    //No partitioned input may launch more threads than required - only load agent data within bounds. 
    if (index < d_xmachine_memory_vertice_count){
    
	agent.id = agents->id[index];
	agent.value = agents->value[index];
	agent.add_value = agents->add_value[index];
	agent.previous = agents->previous[index];
	agent.max_lag = agents->max_lag[index];
	agent.current_lag = agents->current_lag[index];
    agent.edges = &(agents->edges[index]);
	agent.min = agents->min[index];
	agent.max = agents->max[index];
	agent.need_test = agents->need_test[index];
	agent.correct = agents->correct[index];
	} else {
	
	agent.id = 0;
	agent.value = 0;
	agent.add_value = 0;
	agent.previous = 0;
	agent.max_lag = 0;
	agent.current_lag = 0;
    agent.edges = nullptr;
	agent.min = 0;
	agent.max = 0;
	agent.need_test = 0;
	agent.correct = 0;
	}

	//FLAME function call
	int dead = !read_message(&agent, send_local_messages, rand48);
	

	
    //No partitioned input may launch more threads than required - only write agent data within bounds. 
    if (index < d_xmachine_memory_vertice_count){
    //continuous agent: set reallocation flag
	agents->_scan_input[index]  = dead; 

	//AoS to SoA - xmachine_memory_read_message Coalesced memory write (ignore arrays)
	agents->id[index] = agent.id;
	agents->value[index] = agent.value;
	agents->add_value[index] = agent.add_value;
	agents->previous[index] = agent.previous;
	agents->max_lag[index] = agent.max_lag;
	agents->current_lag[index] = agent.current_lag;
	agents->min[index] = agent.min;
	agents->max[index] = agent.max;
	agents->need_test[index] = agent.need_test;
	agents->correct[index] = agent.correct;
	}
}

	

/* Agent ID Generation functions implemented in simulation.cu and FLAMEGPU_kernals.cu*/

__FLAME_GPU_HOST_FUNC__ __FLAME_GPU_FUNC__ int generate_vertice_id(){
#if defined(__CUDA_ARCH__)
	// On the device, use atomicAdd to increment the ID, wrapping at overflow. Does not use atomicInc which only supports unsigned
	int new_id = atomicAdd(&d_current_value_generate_vertice_id, 1);
	return new_id;	
#else
	// On the host, get the current value to be returned and increment the host value.
	int new_id = h_current_value_generate_vertice_id;
	h_current_value_generate_vertice_id++; 
	return new_id;
#endif
}

	
/* Graph utility functions */



/////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/* Rand48 functions */

__device__ static glm::uvec2 RNG_rand48_iterate_single(glm::uvec2 Xn, glm::uvec2 A, glm::uvec2 C)
{
	unsigned int R0, R1;

	// low 24-bit multiplication
	const unsigned int lo00 = __umul24(Xn.x, A.x);
	const unsigned int hi00 = __umulhi(Xn.x, A.x);

	// 24bit distribution of 32bit multiplication results
	R0 = (lo00 & 0xFFFFFF);
	R1 = (lo00 >> 24) | (hi00 << 8);

	R0 += C.x; R1 += C.y;

	// transfer overflows
	R1 += (R0 >> 24);
	R0 &= 0xFFFFFF;

	// cross-terms, low/hi 24-bit multiplication
	R1 += __umul24(Xn.y, A.x);
	R1 += __umul24(Xn.x, A.y);

	R1 &= 0xFFFFFF;

	return glm::uvec2(R0, R1);
}

//Templated function
template <int AGENT_TYPE>
__device__ float rnd(RNG_rand48* rand48){

	int index;
	
	//calculate the agents index in global agent list
	if (AGENT_TYPE == DISCRETE_2D){
		int width = (blockDim.x * gridDim.x);
		glm::ivec2 global_position;
		global_position.x = (blockIdx.x * blockDim.x) + threadIdx.x;
		global_position.y = (blockIdx.y * blockDim.y) + threadIdx.y;
		index = global_position.x + (global_position.y * width);
	}else//AGENT_TYPE == CONTINOUS
		index = threadIdx.x + blockIdx.x*blockDim.x;

	glm::uvec2 state = rand48->seeds[index];
	glm::uvec2 A = rand48->A;
	glm::uvec2 C = rand48->C;

	int rand = ( state.x >> 17 ) | ( state.y << 7);

	// this actually iterates the RNG
	state = RNG_rand48_iterate_single(state, A, C);

	rand48->seeds[index] = state;

	return (float)rand/2147483647;
}

__device__ float rnd(RNG_rand48* rand48){
	return rnd<DISCRETE_2D>(rand48);
}

#endif //_FLAMEGPU_KERNELS_H_
