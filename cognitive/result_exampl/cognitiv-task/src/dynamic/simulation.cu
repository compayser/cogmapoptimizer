
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


  //Disable internal thrust warnings about conversions
  #ifdef _MSC_VER
  #pragma warning(push)
  #pragma warning (disable : 4267)
  #pragma warning (disable : 4244)
  #endif
  #ifdef __GNUC__
  #pragma GCC diagnostic push
  #pragma GCC diagnostic ignored "-Wunused-parameter"
  #endif

  // includes
  #include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <cmath>
#include <thrust/device_ptr.h>
#include <thrust/scan.h>
#include <thrust/sort.h>
#include <thrust/extrema.h>
#include <thrust/system/cuda/execution_policy.h>
#include <cub/cub.cuh>

// include FLAME kernels
#include "FLAMEGPU_kernals.cu"


#ifdef _MSC_VER
#pragma warning(pop)
#endif
#ifdef __GNUC__
#pragma GCC diagnostic pop
#endif

/* Error check function for safe CUDA API calling */
#define gpuErrchk(ans) { gpuAssert((ans), __FILE__, __LINE__); }
inline void gpuAssert(cudaError_t code, const char *file, int line, bool abort=true)
{
   if (code != cudaSuccess) 
   {
      fprintf(stderr,"GPUassert: %s %s %d\n", cudaGetErrorString(code), file, line);
      if (abort) exit(code);
   }
}

/* Error check function for post CUDA Kernel calling */
#define gpuErrchkLaunch() { gpuLaunchAssert(__FILE__, __LINE__); }
inline void gpuLaunchAssert(const char *file, int line, bool abort=true)
{
	gpuAssert( cudaPeekAtLastError(), file, line );
#ifdef _DEBUG
	gpuAssert( cudaDeviceSynchronize(), file, line );
#endif
   
}

/* SM padding and offset variables */
int SM_START;
int PADDING;

unsigned int g_iterationNumber;

/* Agent Memory */

/* vertice Agent variables these lists are used in the agent function where as the other lists are used only outside the agent functions*/
xmachine_memory_vertice_list* d_vertices;      /**< Pointer to agent list (population) on the device*/
xmachine_memory_vertice_list* d_vertices_swap; /**< Pointer to agent list swap on the device (used when killing agents)*/
xmachine_memory_vertice_list* d_vertices_new;  /**< Pointer to new agent list on the device (used to hold new agents before they are appended to the population)*/
int h_xmachine_memory_vertice_count;   /**< Agent population size counter */ 
uint * d_xmachine_memory_vertice_keys;	  /**< Agent sort identifiers keys*/
uint * d_xmachine_memory_vertice_values;  /**< Agent sort identifiers value */

/* vertice state variables */
xmachine_memory_vertice_list* h_vertices_default;      /**< Pointer to agent list (population) on host*/
xmachine_memory_vertice_list* d_vertices_default;      /**< Pointer to agent list (population) on the device*/
int h_xmachine_memory_vertice_default_count;   /**< Agent population size counter */ 


/* Variables to track the state of host copies of state lists, for the purposes of host agent data access.
 * @future - if the host data is current it may be possible to avoid duplicating memcpy in xml output.
 */
unsigned int h_vertices_default_variable_id_data_iteration;
unsigned int h_vertices_default_variable_value_data_iteration;
unsigned int h_vertices_default_variable_add_value_data_iteration;
unsigned int h_vertices_default_variable_previous_data_iteration;
unsigned int h_vertices_default_variable_max_lag_data_iteration;
unsigned int h_vertices_default_variable_current_lag_data_iteration;
unsigned int h_vertices_default_variable_edges_data_iteration;
unsigned int h_vertices_default_variable_min_data_iteration;
unsigned int h_vertices_default_variable_max_data_iteration;
unsigned int h_vertices_default_variable_need_test_data_iteration;
unsigned int h_vertices_default_variable_correct_data_iteration;


/* Message Memory */

/* send_local Message variables */
xmachine_message_send_local_list* h_send_locals;         /**< Pointer to message list on host*/
xmachine_message_send_local_list* d_send_locals;         /**< Pointer to message list on device*/
xmachine_message_send_local_list* d_send_locals_swap;    /**< Pointer to message swap list on device (used for holding optional messages)*/
/* Non partitioned and spatial partitioned message variables  */
int h_message_send_local_count;         /**< message list counter*/
int h_message_send_local_output_type;   /**< message output type (single or optional)*/

  
/* CUDA Streams for function layers */
cudaStream_t stream1;

/* Device memory and sizes for CUB values */

void * d_temp_scan_storage_vertice;
size_t temp_scan_storage_bytes_vertice;


/*Global condition counts*/

/* Agent ID Generation functions implemented in simulation.cu and FLAMEGPU_kernals.cu*/
int h_current_value_generate_vertice_id = 0;

// Track the last value returned from the device, to enable copying to the device after a step function.
int h_last_value_generate_vertice_id = INT_MAX;

void set_initial_vertice_id(int firstID){
  h_current_value_generate_vertice_id = firstID;
}

// Function to copy from the host to the device in the default stream
void update_device_generate_vertice_id(){
// If the last device value doesn't match the current value, update the device value. 
  if(h_current_value_generate_vertice_id != h_last_value_generate_vertice_id){
    gpuErrchk(cudaMemcpyToSymbol( d_current_value_generate_vertice_id, &h_current_value_generate_vertice_id, sizeof(int)));
  }
}
// Function to copy from the device to the host in the default stream
void update_host_generate_vertice_id(){
  gpuErrchk(cudaMemcpyFromSymbol( &h_current_value_generate_vertice_id, d_current_value_generate_vertice_id, sizeof(int)));
  h_last_value_generate_vertice_id = h_current_value_generate_vertice_id;
}



/* RNG rand48 */
RNG_rand48* h_rand48;    /**< Pointer to RNG_rand48 seed list on host*/
RNG_rand48* d_rand48;    /**< Pointer to RNG_rand48 seed list on device*/

/* Early simulation exit*/
bool g_exit_early;

/* Cuda Event Timers for Instrumentation */
#if defined(INSTRUMENT_ITERATIONS) && INSTRUMENT_ITERATIONS
	cudaEvent_t instrument_iteration_start, instrument_iteration_stop;
	float instrument_iteration_milliseconds = 0.0f;
#endif
#if (defined(INSTRUMENT_AGENT_FUNCTIONS) && INSTRUMENT_AGENT_FUNCTIONS) || (defined(INSTRUMENT_INIT_FUNCTIONS) && INSTRUMENT_INIT_FUNCTIONS) || (defined(INSTRUMENT_STEP_FUNCTIONS) && INSTRUMENT_STEP_FUNCTIONS) || (defined(INSTRUMENT_EXIT_FUNCTIONS) && INSTRUMENT_EXIT_FUNCTIONS)
	cudaEvent_t instrument_start, instrument_stop;
	float instrument_milliseconds = 0.0f;
#endif

/* CUDA Parallel Primatives variables */
int scan_last_sum;           /**< Indicates if the position (in message list) of last message*/
int scan_last_included;      /**< Indicates if last sum value is included in the total sum count*/

/* Agent function prototypes */

/** vertice_send_message
 * Agent function prototype for send_message function of vertice agent
 */
void vertice_send_message(cudaStream_t &stream);

/** vertice_read_message
 * Agent function prototype for read_message function of vertice agent
 */
void vertice_read_message(cudaStream_t &stream);

  
void setPaddingAndOffset()
{
    PROFILE_SCOPED_RANGE("setPaddingAndOffset");
	cudaDeviceProp deviceProp;
	cudaGetDeviceProperties(&deviceProp, 0);
	int x64_sys = 0;

	// This function call returns 9999 for both major & minor fields, if no CUDA capable devices are present
	if (deviceProp.major == 9999 && deviceProp.minor == 9999){
		printf("Error: There is no device supporting CUDA.\n");
		exit(EXIT_FAILURE);
	}
    
    //check if double is used and supported
#ifdef _DOUBLE_SUPPORT_REQUIRED_
	printf("Simulation requires full precision double values\n");
	if ((deviceProp.major < 2)&&(deviceProp.minor < 3)){
		printf("Error: Hardware does not support full precision double values!\n");
		exit(EXIT_FAILURE);
	}
    
#endif

	//check 32 or 64bit
	x64_sys = (sizeof(void*)==8);
	if (x64_sys)
	{
		printf("64Bit System Detected\n");
	}
	else
	{
		printf("32Bit System Detected\n");
	}

	SM_START = 0;
	PADDING = 0;
  
	//copy padding and offset to GPU
	gpuErrchk(cudaMemcpyToSymbol( d_SM_START, &SM_START, sizeof(int)));
	gpuErrchk(cudaMemcpyToSymbol( d_PADDING, &PADDING, sizeof(int)));     
}

int is_sqr_pow2(int x){
	int r = (int)pow(4, ceil(log(x)/log(4)));
	return (r == x);
}

int lowest_sqr_pow2(int x){
	int l;
	
	//escape early if x is square power of 2
	if (is_sqr_pow2(x))
		return x;
	
	//lower bound		
	l = (int)pow(4, floor(log(x)/log(4)));
	
	return l;
}

/* Unary function required for cudaOccupancyMaxPotentialBlockSizeVariableSMem to avoid warnings */
int no_sm(int b){
	return 0;
}

/* Unary function to return shared memory size for reorder message kernels */
int reorder_messages_sm_size(int blockSize)
{
	return sizeof(unsigned int)*(blockSize+1);
}


/** getIterationNumber
 *  Get the iteration number (host)
 *  @return a 1 indexed value for the iteration number, which is incremented at the start of each simulation step.
 *      I.e. it is 0 on up until the first call to singleIteration()
 */
extern unsigned int getIterationNumber(){
    return g_iterationNumber;
}

void initialise(char * inputfile){
    PROFILE_SCOPED_RANGE("initialise");

	//set the padding and offset values depending on architecture and OS
	setPaddingAndOffset();
  
		// Initialise some global variables
		g_iterationNumber = 0;
		g_exit_early = false;

    // Initialise variables for tracking which iterations' data is accessible on the host.
    h_vertices_default_variable_id_data_iteration = 0;
    h_vertices_default_variable_value_data_iteration = 0;
    h_vertices_default_variable_add_value_data_iteration = 0;
    h_vertices_default_variable_previous_data_iteration = 0;
    h_vertices_default_variable_max_lag_data_iteration = 0;
    h_vertices_default_variable_current_lag_data_iteration = 0;
    h_vertices_default_variable_edges_data_iteration = 0;
    h_vertices_default_variable_min_data_iteration = 0;
    h_vertices_default_variable_max_data_iteration = 0;
    h_vertices_default_variable_need_test_data_iteration = 0;
    h_vertices_default_variable_correct_data_iteration = 0;
    



	printf("Allocating Host and Device memory\n");
    PROFILE_PUSH_RANGE("allocate host");
	/* Agent memory allocation (CPU) */
	int xmachine_vertice_SoA_size = sizeof(xmachine_memory_vertice_list);
	h_vertices_default = (xmachine_memory_vertice_list*)malloc(xmachine_vertice_SoA_size);

	/* Message memory allocation (CPU) */
	int message_send_local_SoA_size = sizeof(xmachine_message_send_local_list);
	h_send_locals = (xmachine_message_send_local_list*)malloc(message_send_local_SoA_size);

	//Exit if agent or message buffer sizes are to small for function outputs

  /* Graph memory allocation (CPU) */
  

    PROFILE_POP_RANGE(); //"allocate host"
	

	//read initial states
	readInitialStates(inputfile, h_vertices_default, &h_xmachine_memory_vertice_default_count);

  // Read graphs from disk
  

  PROFILE_PUSH_RANGE("allocate device");
	
	/* vertice Agent memory allocation (GPU) */
	gpuErrchk( cudaMalloc( (void**) &d_vertices, xmachine_vertice_SoA_size));
	gpuErrchk( cudaMalloc( (void**) &d_vertices_swap, xmachine_vertice_SoA_size));
	gpuErrchk( cudaMalloc( (void**) &d_vertices_new, xmachine_vertice_SoA_size));
    //continuous agent sort identifiers
  gpuErrchk( cudaMalloc( (void**) &d_xmachine_memory_vertice_keys, xmachine_memory_vertice_MAX* sizeof(uint)));
	gpuErrchk( cudaMalloc( (void**) &d_xmachine_memory_vertice_values, xmachine_memory_vertice_MAX* sizeof(uint)));
	/* default memory allocation (GPU) */
	gpuErrchk( cudaMalloc( (void**) &d_vertices_default, xmachine_vertice_SoA_size));
	gpuErrchk( cudaMemcpy( d_vertices_default, h_vertices_default, xmachine_vertice_SoA_size, cudaMemcpyHostToDevice));
    
	/* send_local Message memory allocation (GPU) */
	gpuErrchk( cudaMalloc( (void**) &d_send_locals, message_send_local_SoA_size));
	gpuErrchk( cudaMalloc( (void**) &d_send_locals_swap, message_send_local_SoA_size));
	gpuErrchk( cudaMemcpy( d_send_locals, h_send_locals, message_send_local_SoA_size, cudaMemcpyHostToDevice));
		


  /* Allocate device memory for graphs */
  

    PROFILE_POP_RANGE(); // "allocate device"

    /* Calculate and allocate CUB temporary memory for exclusive scans */
    
    d_temp_scan_storage_vertice = nullptr;
    temp_scan_storage_bytes_vertice = 0;
    cub::DeviceScan::ExclusiveSum(
        d_temp_scan_storage_vertice, 
        temp_scan_storage_bytes_vertice, 
        (int*) nullptr, 
        (int*) nullptr, 
        xmachine_memory_vertice_MAX
    );
    gpuErrchk(cudaMalloc(&d_temp_scan_storage_vertice, temp_scan_storage_bytes_vertice));
    

	/*Set global condition counts*/

	/* RNG rand48 */
    PROFILE_PUSH_RANGE("Initialse RNG_rand48");
	int h_rand48_SoA_size = sizeof(RNG_rand48);
	h_rand48 = (RNG_rand48*)malloc(h_rand48_SoA_size);
	//allocate on GPU
	gpuErrchk( cudaMalloc( (void**) &d_rand48, h_rand48_SoA_size));
	// calculate strided iteration constants
	static const unsigned long long a = 0x5DEECE66DLL, c = 0xB;
	int seed = 123;
	unsigned long long A, C;
	A = 1LL; C = 0LL;
	for (unsigned int i = 0; i < buffer_size_MAX; ++i) {
		C += A*c;
		A *= a;
	}
	h_rand48->A.x = A & 0xFFFFFFLL;
	h_rand48->A.y = (A >> 24) & 0xFFFFFFLL;
	h_rand48->C.x = C & 0xFFFFFFLL;
	h_rand48->C.y = (C >> 24) & 0xFFFFFFLL;
	// prepare first nThreads random numbers from seed
	unsigned long long x = (((unsigned long long)seed) << 16) | 0x330E;
	for (unsigned int i = 0; i < buffer_size_MAX; ++i) {
		x = a*x + c;
		h_rand48->seeds[i].x = x & 0xFFFFFFLL;
		h_rand48->seeds[i].y = (x >> 24) & 0xFFFFFFLL;
	}
	//copy to device
	gpuErrchk( cudaMemcpy( d_rand48, h_rand48, h_rand48_SoA_size, cudaMemcpyHostToDevice));

    PROFILE_POP_RANGE();

	/* Call all init functions */
	/* Prepare cuda event timers for instrumentation */
#if defined(INSTRUMENT_ITERATIONS) && INSTRUMENT_ITERATIONS
	cudaEventCreate(&instrument_iteration_start);
	cudaEventCreate(&instrument_iteration_stop);
#endif
#if (defined(INSTRUMENT_AGENT_FUNCTIONS) && INSTRUMENT_AGENT_FUNCTIONS) || (defined(INSTRUMENT_INIT_FUNCTIONS) && INSTRUMENT_INIT_FUNCTIONS) || (defined(INSTRUMENT_STEP_FUNCTIONS) && INSTRUMENT_STEP_FUNCTIONS) || (defined(INSTRUMENT_EXIT_FUNCTIONS) && INSTRUMENT_EXIT_FUNCTIONS)
	cudaEventCreate(&instrument_start);
	cudaEventCreate(&instrument_stop);
#endif

	

  /* If any Agents can generate IDs, update the device value after init functions have executed */

  update_device_generate_vertice_id();

  
  /* Init CUDA Streams for function layers */
  
  gpuErrchk(cudaStreamCreate(&stream1));

#if defined(OUTPUT_POPULATION_PER_ITERATION) && OUTPUT_POPULATION_PER_ITERATION
	// Print the agent population size of all agents in all states
	
		printf("Init agent_vertice_default_count: %u\n",get_agent_vertice_default_count());
	
#endif
} 


void sort_vertices_default(void (*generate_key_value_pairs)(unsigned int* keys, unsigned int* values, xmachine_memory_vertice_list* agents))
{
	int blockSize;
	int minGridSize;
	int gridSize;

	//generate sort keys
	cudaOccupancyMaxPotentialBlockSizeVariableSMem( &minGridSize, &blockSize, generate_key_value_pairs, no_sm, h_xmachine_memory_vertice_default_count); 
	gridSize = (h_xmachine_memory_vertice_default_count + blockSize - 1) / blockSize;    // Round up according to array size 
	generate_key_value_pairs<<<gridSize, blockSize>>>(d_xmachine_memory_vertice_keys, d_xmachine_memory_vertice_values, d_vertices_default);
	gpuErrchkLaunch();

	//updated Thrust sort
	thrust::sort_by_key( thrust::device_pointer_cast(d_xmachine_memory_vertice_keys),  thrust::device_pointer_cast(d_xmachine_memory_vertice_keys) + h_xmachine_memory_vertice_default_count,  thrust::device_pointer_cast(d_xmachine_memory_vertice_values));
	gpuErrchkLaunch();

	//reorder agents
	cudaOccupancyMaxPotentialBlockSizeVariableSMem( &minGridSize, &blockSize, reorder_vertice_agents, no_sm, h_xmachine_memory_vertice_default_count); 
	gridSize = (h_xmachine_memory_vertice_default_count + blockSize - 1) / blockSize;    // Round up according to array size 
	reorder_vertice_agents<<<gridSize, blockSize>>>(d_xmachine_memory_vertice_values, d_vertices_default, d_vertices_swap);
	gpuErrchkLaunch();

	//swap
	xmachine_memory_vertice_list* d_vertices_temp = d_vertices_default;
	d_vertices_default = d_vertices_swap;
	d_vertices_swap = d_vertices_temp;	
}


void cleanup(){
    PROFILE_SCOPED_RANGE("cleanup");

    /* Call all exit functions */
	

	/* Agent data free*/
	
	/* vertice Agent variables */
	gpuErrchk(cudaFree(d_vertices));
	gpuErrchk(cudaFree(d_vertices_swap));
	gpuErrchk(cudaFree(d_vertices_new));
	
	free( h_vertices_default);
	gpuErrchk(cudaFree(d_vertices_default));
	

	/* Message data free */
	
	/* send_local Message variables */
	free( h_send_locals);
	gpuErrchk(cudaFree(d_send_locals));
	gpuErrchk(cudaFree(d_send_locals_swap));
	

    /* Free temporary CUB memory if required. */
    
    if(d_temp_scan_storage_vertice != nullptr){
      gpuErrchk(cudaFree(d_temp_scan_storage_vertice));
      d_temp_scan_storage_vertice = nullptr;
      temp_scan_storage_bytes_vertice = 0;
    }
    

  /* Graph data free */
  
  
  /* CUDA Streams for function layers */
  
  gpuErrchk(cudaStreamDestroy(stream1));

  /* CUDA Event Timers for Instrumentation */
#if defined(INSTRUMENT_ITERATIONS) && INSTRUMENT_ITERATIONS
	cudaEventDestroy(instrument_iteration_start);
	cudaEventDestroy(instrument_iteration_stop);
#endif
#if (defined(INSTRUMENT_AGENT_FUNCTIONS) && INSTRUMENT_AGENT_FUNCTIONS) || (defined(INSTRUMENT_INIT_FUNCTIONS) && INSTRUMENT_INIT_FUNCTIONS) || (defined(INSTRUMENT_STEP_FUNCTIONS) && INSTRUMENT_STEP_FUNCTIONS) || (defined(INSTRUMENT_EXIT_FUNCTIONS) && INSTRUMENT_EXIT_FUNCTIONS)
	cudaEventDestroy(instrument_start);
	cudaEventDestroy(instrument_stop);
#endif
}

void singleIteration(){
PROFILE_SCOPED_RANGE("singleIteration");

#if defined(INSTRUMENT_ITERATIONS) && INSTRUMENT_ITERATIONS
	cudaEventRecord(instrument_iteration_start);
#endif

    // Increment the iteration number.
    g_iterationNumber++;

  /* set all non partitioned, spatial partitioned and On-Graph Partitioned message counts to 0*/
	h_message_send_local_count = 0;
	//upload to device constant
	gpuErrchk(cudaMemcpyToSymbol( d_message_send_local_count, &h_message_send_local_count, sizeof(int)));
	

	/* Call agent functions in order iterating through the layer functions */
	
	/* Layer 1*/
	
#if defined(INSTRUMENT_AGENT_FUNCTIONS) && INSTRUMENT_AGENT_FUNCTIONS
	cudaEventRecord(instrument_start);
#endif
	
    PROFILE_PUSH_RANGE("vertice_send_message");
	vertice_send_message(stream1);
    PROFILE_POP_RANGE();
#if defined(INSTRUMENT_AGENT_FUNCTIONS) && INSTRUMENT_AGENT_FUNCTIONS
	cudaEventRecord(instrument_stop);
	cudaEventSynchronize(instrument_stop);
	cudaEventElapsedTime(&instrument_milliseconds, instrument_start, instrument_stop);
	printf("Instrumentation: vertice_send_message = %f (ms)\n", instrument_milliseconds);
#endif
	cudaDeviceSynchronize();
  
	/* Layer 2*/
	
#if defined(INSTRUMENT_AGENT_FUNCTIONS) && INSTRUMENT_AGENT_FUNCTIONS
	cudaEventRecord(instrument_start);
#endif
	
    PROFILE_PUSH_RANGE("vertice_read_message");
	vertice_read_message(stream1);
    PROFILE_POP_RANGE();
#if defined(INSTRUMENT_AGENT_FUNCTIONS) && INSTRUMENT_AGENT_FUNCTIONS
	cudaEventRecord(instrument_stop);
	cudaEventSynchronize(instrument_stop);
	cudaEventElapsedTime(&instrument_milliseconds, instrument_start, instrument_stop);
	printf("Instrumentation: vertice_read_message = %f (ms)\n", instrument_milliseconds);
#endif
	cudaDeviceSynchronize();
  

  /* If any Agents can generate IDs, update the host value after agent functions have executed */

  update_host_generate_vertice_id();

    
    /* Call all step functions */
	

/* If any Agents can generate IDs, update the device value after step functions have executed */

  update_device_generate_vertice_id();


#if defined(OUTPUT_POPULATION_PER_ITERATION) && OUTPUT_POPULATION_PER_ITERATION
	// Print the agent population size of all agents in all states
	
		printf("agent_vertice_default_count: %u\n",get_agent_vertice_default_count());
	
#endif

#if defined(INSTRUMENT_ITERATIONS) && INSTRUMENT_ITERATIONS
	cudaEventRecord(instrument_iteration_stop);
	cudaEventSynchronize(instrument_iteration_stop);
	cudaEventElapsedTime(&instrument_iteration_milliseconds, instrument_iteration_start, instrument_iteration_stop);
	printf("Instrumentation: Iteration Time = %f (ms)\n", instrument_iteration_milliseconds);
#endif
}

/* finish whole simulation after this step */
void set_exit_early() {
	g_exit_early = true;
}

bool get_exit_early() {
	return g_exit_early;
}

/* Environment functions */

//host constant declaration
int h_env_VERTICES_COUNT;


//constant setter
void set_VERTICES_COUNT(int* h_VERTICES_COUNT){
    gpuErrchk(cudaMemcpyToSymbol(VERTICES_COUNT, h_VERTICES_COUNT, sizeof(int)));
    memcpy(&h_env_VERTICES_COUNT, h_VERTICES_COUNT,sizeof(int));
}

//constant getter
const int* get_VERTICES_COUNT(){
    return &h_env_VERTICES_COUNT;
}




/* Agent data access functions*/

    
int get_agent_vertice_MAX_count(){
    return xmachine_memory_vertice_MAX;
}


int get_agent_vertice_default_count(){
	//continuous agent
	return h_xmachine_memory_vertice_default_count;
	
}

xmachine_memory_vertice_list* get_device_vertice_default_agents(){
	return d_vertices_default;
}

xmachine_memory_vertice_list* get_host_vertice_default_agents(){
	return h_vertices_default;
}



/* Host based access of agent variables*/

/** int get_vertice_default_variable_id(unsigned int index)
 * Gets the value of the id variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable id
 */
__host__ int get_vertice_default_variable_id(unsigned int index){
    unsigned int count = get_agent_vertice_default_count();
    unsigned int currentIteration = getIterationNumber();
    
    // If the index is within bounds - no need to check >= 0 due to unsigned.
    if(count > 0 && index < count ){
        // If necessary, copy agent data from the device to the host in the default stream
        if(h_vertices_default_variable_id_data_iteration != currentIteration){
            gpuErrchk(
                cudaMemcpy(
                    h_vertices_default->id,
                    d_vertices_default->id,
                    count * sizeof(int),
                    cudaMemcpyDeviceToHost
                )
            );
            // Update some global value indicating what data is currently present in that host array.
            h_vertices_default_variable_id_data_iteration = currentIteration;
        }

        // Return the value of the index-th element of the relevant host array.
        return h_vertices_default->id[index];

    } else {
        fprintf(stderr, "Warning: Attempting to access id for the %u th member of vertice_default. count is %u at iteration %u\n", index, count, currentIteration);
        // Otherwise we return a default value
        return 0;

    }
}

/** float get_vertice_default_variable_value(unsigned int index)
 * Gets the value of the value variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable value
 */
__host__ float get_vertice_default_variable_value(unsigned int index){
    unsigned int count = get_agent_vertice_default_count();
    unsigned int currentIteration = getIterationNumber();
    
    // If the index is within bounds - no need to check >= 0 due to unsigned.
    if(count > 0 && index < count ){
        // If necessary, copy agent data from the device to the host in the default stream
        if(h_vertices_default_variable_value_data_iteration != currentIteration){
            gpuErrchk(
                cudaMemcpy(
                    h_vertices_default->value,
                    d_vertices_default->value,
                    count * sizeof(float),
                    cudaMemcpyDeviceToHost
                )
            );
            // Update some global value indicating what data is currently present in that host array.
            h_vertices_default_variable_value_data_iteration = currentIteration;
        }

        // Return the value of the index-th element of the relevant host array.
        return h_vertices_default->value[index];

    } else {
        fprintf(stderr, "Warning: Attempting to access value for the %u th member of vertice_default. count is %u at iteration %u\n", index, count, currentIteration);
        // Otherwise we return a default value
        return 0;

    }
}

/** float get_vertice_default_variable_add_value(unsigned int index)
 * Gets the value of the add_value variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable add_value
 */
__host__ float get_vertice_default_variable_add_value(unsigned int index){
    unsigned int count = get_agent_vertice_default_count();
    unsigned int currentIteration = getIterationNumber();
    
    // If the index is within bounds - no need to check >= 0 due to unsigned.
    if(count > 0 && index < count ){
        // If necessary, copy agent data from the device to the host in the default stream
        if(h_vertices_default_variable_add_value_data_iteration != currentIteration){
            gpuErrchk(
                cudaMemcpy(
                    h_vertices_default->add_value,
                    d_vertices_default->add_value,
                    count * sizeof(float),
                    cudaMemcpyDeviceToHost
                )
            );
            // Update some global value indicating what data is currently present in that host array.
            h_vertices_default_variable_add_value_data_iteration = currentIteration;
        }

        // Return the value of the index-th element of the relevant host array.
        return h_vertices_default->add_value[index];

    } else {
        fprintf(stderr, "Warning: Attempting to access add_value for the %u th member of vertice_default. count is %u at iteration %u\n", index, count, currentIteration);
        // Otherwise we return a default value
        return 0;

    }
}

/** float get_vertice_default_variable_previous(unsigned int index)
 * Gets the value of the previous variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable previous
 */
__host__ float get_vertice_default_variable_previous(unsigned int index){
    unsigned int count = get_agent_vertice_default_count();
    unsigned int currentIteration = getIterationNumber();
    
    // If the index is within bounds - no need to check >= 0 due to unsigned.
    if(count > 0 && index < count ){
        // If necessary, copy agent data from the device to the host in the default stream
        if(h_vertices_default_variable_previous_data_iteration != currentIteration){
            gpuErrchk(
                cudaMemcpy(
                    h_vertices_default->previous,
                    d_vertices_default->previous,
                    count * sizeof(float),
                    cudaMemcpyDeviceToHost
                )
            );
            // Update some global value indicating what data is currently present in that host array.
            h_vertices_default_variable_previous_data_iteration = currentIteration;
        }

        // Return the value of the index-th element of the relevant host array.
        return h_vertices_default->previous[index];

    } else {
        fprintf(stderr, "Warning: Attempting to access previous for the %u th member of vertice_default. count is %u at iteration %u\n", index, count, currentIteration);
        // Otherwise we return a default value
        return 0;

    }
}

/** int get_vertice_default_variable_max_lag(unsigned int index)
 * Gets the value of the max_lag variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable max_lag
 */
__host__ int get_vertice_default_variable_max_lag(unsigned int index){
    unsigned int count = get_agent_vertice_default_count();
    unsigned int currentIteration = getIterationNumber();
    
    // If the index is within bounds - no need to check >= 0 due to unsigned.
    if(count > 0 && index < count ){
        // If necessary, copy agent data from the device to the host in the default stream
        if(h_vertices_default_variable_max_lag_data_iteration != currentIteration){
            gpuErrchk(
                cudaMemcpy(
                    h_vertices_default->max_lag,
                    d_vertices_default->max_lag,
                    count * sizeof(int),
                    cudaMemcpyDeviceToHost
                )
            );
            // Update some global value indicating what data is currently present in that host array.
            h_vertices_default_variable_max_lag_data_iteration = currentIteration;
        }

        // Return the value of the index-th element of the relevant host array.
        return h_vertices_default->max_lag[index];

    } else {
        fprintf(stderr, "Warning: Attempting to access max_lag for the %u th member of vertice_default. count is %u at iteration %u\n", index, count, currentIteration);
        // Otherwise we return a default value
        return 0;

    }
}

/** int get_vertice_default_variable_current_lag(unsigned int index)
 * Gets the value of the current_lag variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable current_lag
 */
__host__ int get_vertice_default_variable_current_lag(unsigned int index){
    unsigned int count = get_agent_vertice_default_count();
    unsigned int currentIteration = getIterationNumber();
    
    // If the index is within bounds - no need to check >= 0 due to unsigned.
    if(count > 0 && index < count ){
        // If necessary, copy agent data from the device to the host in the default stream
        if(h_vertices_default_variable_current_lag_data_iteration != currentIteration){
            gpuErrchk(
                cudaMemcpy(
                    h_vertices_default->current_lag,
                    d_vertices_default->current_lag,
                    count * sizeof(int),
                    cudaMemcpyDeviceToHost
                )
            );
            // Update some global value indicating what data is currently present in that host array.
            h_vertices_default_variable_current_lag_data_iteration = currentIteration;
        }

        // Return the value of the index-th element of the relevant host array.
        return h_vertices_default->current_lag[index];

    } else {
        fprintf(stderr, "Warning: Attempting to access current_lag for the %u th member of vertice_default. count is %u at iteration %u\n", index, count, currentIteration);
        // Otherwise we return a default value
        return 0;

    }
}

/** float get_vertice_default_variable_edges(unsigned int index, unsigned int element)
 * Gets the element-th value of the edges variable array of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @param element the element index within the variable array
 * @return element-th value of agent variable edges
 */
__host__ float get_vertice_default_variable_edges(unsigned int index, unsigned int element){
    unsigned int count = get_agent_vertice_default_count();
    unsigned int numElements = 17;
    unsigned int currentIteration = getIterationNumber();
    
    // If the index is within bounds - no need to check >= 0 due to unsigned.
    if(count > 0 && index < count && element < numElements ){
        // If necessary, copy agent data from the device to the host in the default stream
        if(h_vertices_default_variable_edges_data_iteration != currentIteration){
            
            for(unsigned int e = 0; e < numElements; e++){
                gpuErrchk(
                    cudaMemcpy(
                        h_vertices_default->edges + (e * xmachine_memory_vertice_MAX),
                        d_vertices_default->edges + (e * xmachine_memory_vertice_MAX), 
                        count * sizeof(float), 
                        cudaMemcpyDeviceToHost
                    )
                );
                // Update some global value indicating what data is currently present in that host array.
                h_vertices_default_variable_edges_data_iteration = currentIteration;
            }
        }

        // Return the value of the index-th element of the relevant host array.
        return h_vertices_default->edges[index + (element * xmachine_memory_vertice_MAX)];

    } else {
        fprintf(stderr, "Warning: Attempting to access the %u-th element of edges for the %u th member of vertice_default. count is %u at iteration %u\n", element, index, count, currentIteration);
        // Otherwise we return a default value
        return 0;

    }
}

/** float get_vertice_default_variable_min(unsigned int index)
 * Gets the value of the min variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable min
 */
__host__ float get_vertice_default_variable_min(unsigned int index){
    unsigned int count = get_agent_vertice_default_count();
    unsigned int currentIteration = getIterationNumber();
    
    // If the index is within bounds - no need to check >= 0 due to unsigned.
    if(count > 0 && index < count ){
        // If necessary, copy agent data from the device to the host in the default stream
        if(h_vertices_default_variable_min_data_iteration != currentIteration){
            gpuErrchk(
                cudaMemcpy(
                    h_vertices_default->min,
                    d_vertices_default->min,
                    count * sizeof(float),
                    cudaMemcpyDeviceToHost
                )
            );
            // Update some global value indicating what data is currently present in that host array.
            h_vertices_default_variable_min_data_iteration = currentIteration;
        }

        // Return the value of the index-th element of the relevant host array.
        return h_vertices_default->min[index];

    } else {
        fprintf(stderr, "Warning: Attempting to access min for the %u th member of vertice_default. count is %u at iteration %u\n", index, count, currentIteration);
        // Otherwise we return a default value
        return 0;

    }
}

/** float get_vertice_default_variable_max(unsigned int index)
 * Gets the value of the max variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable max
 */
__host__ float get_vertice_default_variable_max(unsigned int index){
    unsigned int count = get_agent_vertice_default_count();
    unsigned int currentIteration = getIterationNumber();
    
    // If the index is within bounds - no need to check >= 0 due to unsigned.
    if(count > 0 && index < count ){
        // If necessary, copy agent data from the device to the host in the default stream
        if(h_vertices_default_variable_max_data_iteration != currentIteration){
            gpuErrchk(
                cudaMemcpy(
                    h_vertices_default->max,
                    d_vertices_default->max,
                    count * sizeof(float),
                    cudaMemcpyDeviceToHost
                )
            );
            // Update some global value indicating what data is currently present in that host array.
            h_vertices_default_variable_max_data_iteration = currentIteration;
        }

        // Return the value of the index-th element of the relevant host array.
        return h_vertices_default->max[index];

    } else {
        fprintf(stderr, "Warning: Attempting to access max for the %u th member of vertice_default. count is %u at iteration %u\n", index, count, currentIteration);
        // Otherwise we return a default value
        return 0;

    }
}

/** int get_vertice_default_variable_need_test(unsigned int index)
 * Gets the value of the need_test variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable need_test
 */
__host__ int get_vertice_default_variable_need_test(unsigned int index){
    unsigned int count = get_agent_vertice_default_count();
    unsigned int currentIteration = getIterationNumber();
    
    // If the index is within bounds - no need to check >= 0 due to unsigned.
    if(count > 0 && index < count ){
        // If necessary, copy agent data from the device to the host in the default stream
        if(h_vertices_default_variable_need_test_data_iteration != currentIteration){
            gpuErrchk(
                cudaMemcpy(
                    h_vertices_default->need_test,
                    d_vertices_default->need_test,
                    count * sizeof(int),
                    cudaMemcpyDeviceToHost
                )
            );
            // Update some global value indicating what data is currently present in that host array.
            h_vertices_default_variable_need_test_data_iteration = currentIteration;
        }

        // Return the value of the index-th element of the relevant host array.
        return h_vertices_default->need_test[index];

    } else {
        fprintf(stderr, "Warning: Attempting to access need_test for the %u th member of vertice_default. count is %u at iteration %u\n", index, count, currentIteration);
        // Otherwise we return a default value
        return 0;

    }
}

/** int get_vertice_default_variable_correct(unsigned int index)
 * Gets the value of the correct variable of an vertice agent in the default state on the host. 
 * If the data is not currently on the host, a memcpy of the data of all agents in that state list will be issued, via a global.
 * This has a potentially significant performance impact if used improperly.
 * @param index the index of the agent within the list.
 * @return value of agent variable correct
 */
__host__ int get_vertice_default_variable_correct(unsigned int index){
    unsigned int count = get_agent_vertice_default_count();
    unsigned int currentIteration = getIterationNumber();
    
    // If the index is within bounds - no need to check >= 0 due to unsigned.
    if(count > 0 && index < count ){
        // If necessary, copy agent data from the device to the host in the default stream
        if(h_vertices_default_variable_correct_data_iteration != currentIteration){
            gpuErrchk(
                cudaMemcpy(
                    h_vertices_default->correct,
                    d_vertices_default->correct,
                    count * sizeof(int),
                    cudaMemcpyDeviceToHost
                )
            );
            // Update some global value indicating what data is currently present in that host array.
            h_vertices_default_variable_correct_data_iteration = currentIteration;
        }

        // Return the value of the index-th element of the relevant host array.
        return h_vertices_default->correct[index];

    } else {
        fprintf(stderr, "Warning: Attempting to access correct for the %u th member of vertice_default. count is %u at iteration %u\n", index, count, currentIteration);
        // Otherwise we return a default value
        return 0;

    }
}



/* Host based agent creation functions */
// These are only available for continuous agents.



/* copy_single_xmachine_memory_vertice_hostToDevice
 * Private function to copy a host agent struct into a device SoA agent list.
 * @param d_dst destination agent state list
 * @param h_agent agent struct
 */
void copy_single_xmachine_memory_vertice_hostToDevice(xmachine_memory_vertice_list * d_dst, xmachine_memory_vertice * h_agent){
 
		gpuErrchk(cudaMemcpy(d_dst->id, &h_agent->id, sizeof(int), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->value, &h_agent->value, sizeof(float), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->add_value, &h_agent->add_value, sizeof(float), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->previous, &h_agent->previous, sizeof(float), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->max_lag, &h_agent->max_lag, sizeof(int), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->current_lag, &h_agent->current_lag, sizeof(int), cudaMemcpyHostToDevice));
 
	for(unsigned int i = 0; i < 17; i++){
		gpuErrchk(cudaMemcpy(d_dst->edges + (i * xmachine_memory_vertice_MAX), h_agent->edges + i, sizeof(float), cudaMemcpyHostToDevice));
    }
 
		gpuErrchk(cudaMemcpy(d_dst->min, &h_agent->min, sizeof(float), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->max, &h_agent->max, sizeof(float), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->need_test, &h_agent->need_test, sizeof(int), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->correct, &h_agent->correct, sizeof(int), cudaMemcpyHostToDevice));

}
/*
 * Private function to copy some elements from a host based struct of arrays to a device based struct of arrays for a single agent state.
 * Individual copies of `count` elements are performed for each agent variable or each component of agent array variables, to avoid wasted data transfer.
 * There will be a point at which a single cudaMemcpy will outperform many smaller memcpys, however host based agent creation should typically only populate a fraction of the maximum buffer size, so this should be more efficient.
 * @optimisation - experimentally find the proportion at which transferring the whole SoA would be better and incorporate this. The same will apply to agent variable arrays.
 * 
 * @param d_dst device destination SoA
 * @oaram h_src host source SoA
 * @param count the number of agents to transfer data for
 */
void copy_partial_xmachine_memory_vertice_hostToDevice(xmachine_memory_vertice_list * d_dst, xmachine_memory_vertice_list * h_src, unsigned int count){
    // Only copy elements if there is data to move.
    if (count > 0){
	 
		gpuErrchk(cudaMemcpy(d_dst->id, h_src->id, count * sizeof(int), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->value, h_src->value, count * sizeof(float), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->add_value, h_src->add_value, count * sizeof(float), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->previous, h_src->previous, count * sizeof(float), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->max_lag, h_src->max_lag, count * sizeof(int), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->current_lag, h_src->current_lag, count * sizeof(int), cudaMemcpyHostToDevice));
 
		for(unsigned int i = 0; i < 17; i++){
			gpuErrchk(cudaMemcpy(d_dst->edges + (i * xmachine_memory_vertice_MAX), h_src->edges + (i * xmachine_memory_vertice_MAX), count * sizeof(float), cudaMemcpyHostToDevice));
        }

 
		gpuErrchk(cudaMemcpy(d_dst->min, h_src->min, count * sizeof(float), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->max, h_src->max, count * sizeof(float), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->need_test, h_src->need_test, count * sizeof(int), cudaMemcpyHostToDevice));
 
		gpuErrchk(cudaMemcpy(d_dst->correct, h_src->correct, count * sizeof(int), cudaMemcpyHostToDevice));

    }
}

xmachine_memory_vertice* h_allocate_agent_vertice(){
	xmachine_memory_vertice* agent = (xmachine_memory_vertice*)malloc(sizeof(xmachine_memory_vertice));
	// Memset the whole agent strcuture
    memset(agent, 0, sizeof(xmachine_memory_vertice));

    agent->add_value = 0;

    agent->current_lag = 0;
	// Agent variable arrays must be allocated
    agent->edges = (float*)malloc(17 * sizeof(float));
	
    // If there is no default value, memset to 0.
    memset(agent->edges, 0, sizeof(float)*17);
	return agent;
}
void h_free_agent_vertice(xmachine_memory_vertice** agent){

    free((*agent)->edges);
 
	free((*agent));
	(*agent) = NULL;
}
xmachine_memory_vertice** h_allocate_agent_vertice_array(unsigned int count){
	xmachine_memory_vertice ** agents = (xmachine_memory_vertice**)malloc(count * sizeof(xmachine_memory_vertice*));
	for (unsigned int i = 0; i < count; i++) {
		agents[i] = h_allocate_agent_vertice();
	}
	return agents;
}
void h_free_agent_vertice_array(xmachine_memory_vertice*** agents, unsigned int count){
	for (unsigned int i = 0; i < count; i++) {
		h_free_agent_vertice(&((*agents)[i]));
	}
	free((*agents));
	(*agents) = NULL;
}

void h_unpack_agents_vertice_AoS_to_SoA(xmachine_memory_vertice_list * dst, xmachine_memory_vertice** src, unsigned int count){
	if(count > 0){
		for(unsigned int i = 0; i < count; i++){
			 
			dst->id[i] = src[i]->id;
			 
			dst->value[i] = src[i]->value;
			 
			dst->add_value[i] = src[i]->add_value;
			 
			dst->previous[i] = src[i]->previous;
			 
			dst->max_lag[i] = src[i]->max_lag;
			 
			dst->current_lag[i] = src[i]->current_lag;
			 
			for(unsigned int j = 0; j < 17; j++){
				dst->edges[(j * xmachine_memory_vertice_MAX) + i] = src[i]->edges[j];
			}
			 
			dst->min[i] = src[i]->min;
			 
			dst->max[i] = src[i]->max;
			 
			dst->need_test[i] = src[i]->need_test;
			 
			dst->correct[i] = src[i]->correct;
			
		}
	}
}


void h_add_agent_vertice_default(xmachine_memory_vertice* agent){
	if (h_xmachine_memory_vertice_count + 1 > xmachine_memory_vertice_MAX){
		printf("Error: Buffer size of vertice agents in state default will be exceeded by h_add_agent_vertice_default\n");
		exit(EXIT_FAILURE);
	}	

	int blockSize;
	int minGridSize;
	int gridSize;
	unsigned int count = 1;
	
	// Copy data from host struct to device SoA for target state
	copy_single_xmachine_memory_vertice_hostToDevice(d_vertices_new, agent);

	// Use append kernel (@optimisation - This can be replaced with a pointer swap if the target state list is empty)
	cudaOccupancyMaxPotentialBlockSizeVariableSMem(&minGridSize, &blockSize, append_vertice_Agents, no_sm, count);
	gridSize = (count + blockSize - 1) / blockSize;
	append_vertice_Agents <<<gridSize, blockSize, 0, stream1 >>>(d_vertices_default, d_vertices_new, h_xmachine_memory_vertice_default_count, count);
	gpuErrchkLaunch();
	// Update the number of agents in this state.
	h_xmachine_memory_vertice_default_count += count;
	gpuErrchk(cudaMemcpyToSymbol(d_xmachine_memory_vertice_default_count, &h_xmachine_memory_vertice_default_count, sizeof(int)));
	cudaDeviceSynchronize();

    // Reset host variable status flags for the relevant agent state list as the device state list has been modified.
    h_vertices_default_variable_id_data_iteration = 0;
    h_vertices_default_variable_value_data_iteration = 0;
    h_vertices_default_variable_add_value_data_iteration = 0;
    h_vertices_default_variable_previous_data_iteration = 0;
    h_vertices_default_variable_max_lag_data_iteration = 0;
    h_vertices_default_variable_current_lag_data_iteration = 0;
    h_vertices_default_variable_edges_data_iteration = 0;
    h_vertices_default_variable_min_data_iteration = 0;
    h_vertices_default_variable_max_data_iteration = 0;
    h_vertices_default_variable_need_test_data_iteration = 0;
    h_vertices_default_variable_correct_data_iteration = 0;
    

}
void h_add_agents_vertice_default(xmachine_memory_vertice** agents, unsigned int count){
	if(count > 0){
		int blockSize;
		int minGridSize;
		int gridSize;

		if (h_xmachine_memory_vertice_count + count > xmachine_memory_vertice_MAX){
			printf("Error: Buffer size of vertice agents in state default will be exceeded by h_add_agents_vertice_default\n");
			exit(EXIT_FAILURE);
		}

		// Unpack data from AoS into the pre-existing SoA
		h_unpack_agents_vertice_AoS_to_SoA(h_vertices_default, agents, count);

		// Copy data from the host SoA to the device SoA for the target state
		copy_partial_xmachine_memory_vertice_hostToDevice(d_vertices_new, h_vertices_default, count);

		// Use append kernel (@optimisation - This can be replaced with a pointer swap if the target state list is empty)
		cudaOccupancyMaxPotentialBlockSizeVariableSMem(&minGridSize, &blockSize, append_vertice_Agents, no_sm, count);
		gridSize = (count + blockSize - 1) / blockSize;
		append_vertice_Agents <<<gridSize, blockSize, 0, stream1 >>>(d_vertices_default, d_vertices_new, h_xmachine_memory_vertice_default_count, count);
		gpuErrchkLaunch();
		// Update the number of agents in this state.
		h_xmachine_memory_vertice_default_count += count;
		gpuErrchk(cudaMemcpyToSymbol(d_xmachine_memory_vertice_default_count, &h_xmachine_memory_vertice_default_count, sizeof(int)));
		cudaDeviceSynchronize();

        // Reset host variable status flags for the relevant agent state list as the device state list has been modified.
        h_vertices_default_variable_id_data_iteration = 0;
        h_vertices_default_variable_value_data_iteration = 0;
        h_vertices_default_variable_add_value_data_iteration = 0;
        h_vertices_default_variable_previous_data_iteration = 0;
        h_vertices_default_variable_max_lag_data_iteration = 0;
        h_vertices_default_variable_current_lag_data_iteration = 0;
        h_vertices_default_variable_edges_data_iteration = 0;
        h_vertices_default_variable_min_data_iteration = 0;
        h_vertices_default_variable_max_data_iteration = 0;
        h_vertices_default_variable_need_test_data_iteration = 0;
        h_vertices_default_variable_correct_data_iteration = 0;
        

	}
}


/*  Analytics Functions */

int reduce_vertice_default_id_variable(){
    //reduce in default stream
    return thrust::reduce(thrust::device_pointer_cast(d_vertices_default->id),  thrust::device_pointer_cast(d_vertices_default->id) + h_xmachine_memory_vertice_default_count);
}

int count_vertice_default_id_variable(int count_value){
    //count in default stream
    return (int)thrust::count(thrust::device_pointer_cast(d_vertices_default->id),  thrust::device_pointer_cast(d_vertices_default->id) + h_xmachine_memory_vertice_default_count, count_value);
}
int min_vertice_default_id_variable(){
    //min in default stream
    thrust::device_ptr<int> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->id);
    size_t result_offset = thrust::min_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
int max_vertice_default_id_variable(){
    //max in default stream
    thrust::device_ptr<int> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->id);
    size_t result_offset = thrust::max_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
float reduce_vertice_default_value_variable(){
    //reduce in default stream
    return thrust::reduce(thrust::device_pointer_cast(d_vertices_default->value),  thrust::device_pointer_cast(d_vertices_default->value) + h_xmachine_memory_vertice_default_count);
}

float min_vertice_default_value_variable(){
    //min in default stream
    thrust::device_ptr<float> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->value);
    size_t result_offset = thrust::min_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
float max_vertice_default_value_variable(){
    //max in default stream
    thrust::device_ptr<float> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->value);
    size_t result_offset = thrust::max_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
float reduce_vertice_default_add_value_variable(){
    //reduce in default stream
    return thrust::reduce(thrust::device_pointer_cast(d_vertices_default->add_value),  thrust::device_pointer_cast(d_vertices_default->add_value) + h_xmachine_memory_vertice_default_count);
}

float min_vertice_default_add_value_variable(){
    //min in default stream
    thrust::device_ptr<float> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->add_value);
    size_t result_offset = thrust::min_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
float max_vertice_default_add_value_variable(){
    //max in default stream
    thrust::device_ptr<float> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->add_value);
    size_t result_offset = thrust::max_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
float reduce_vertice_default_previous_variable(){
    //reduce in default stream
    return thrust::reduce(thrust::device_pointer_cast(d_vertices_default->previous),  thrust::device_pointer_cast(d_vertices_default->previous) + h_xmachine_memory_vertice_default_count);
}

float min_vertice_default_previous_variable(){
    //min in default stream
    thrust::device_ptr<float> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->previous);
    size_t result_offset = thrust::min_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
float max_vertice_default_previous_variable(){
    //max in default stream
    thrust::device_ptr<float> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->previous);
    size_t result_offset = thrust::max_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
int reduce_vertice_default_max_lag_variable(){
    //reduce in default stream
    return thrust::reduce(thrust::device_pointer_cast(d_vertices_default->max_lag),  thrust::device_pointer_cast(d_vertices_default->max_lag) + h_xmachine_memory_vertice_default_count);
}

int count_vertice_default_max_lag_variable(int count_value){
    //count in default stream
    return (int)thrust::count(thrust::device_pointer_cast(d_vertices_default->max_lag),  thrust::device_pointer_cast(d_vertices_default->max_lag) + h_xmachine_memory_vertice_default_count, count_value);
}
int min_vertice_default_max_lag_variable(){
    //min in default stream
    thrust::device_ptr<int> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->max_lag);
    size_t result_offset = thrust::min_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
int max_vertice_default_max_lag_variable(){
    //max in default stream
    thrust::device_ptr<int> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->max_lag);
    size_t result_offset = thrust::max_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
int reduce_vertice_default_current_lag_variable(){
    //reduce in default stream
    return thrust::reduce(thrust::device_pointer_cast(d_vertices_default->current_lag),  thrust::device_pointer_cast(d_vertices_default->current_lag) + h_xmachine_memory_vertice_default_count);
}

int count_vertice_default_current_lag_variable(int count_value){
    //count in default stream
    return (int)thrust::count(thrust::device_pointer_cast(d_vertices_default->current_lag),  thrust::device_pointer_cast(d_vertices_default->current_lag) + h_xmachine_memory_vertice_default_count, count_value);
}
int min_vertice_default_current_lag_variable(){
    //min in default stream
    thrust::device_ptr<int> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->current_lag);
    size_t result_offset = thrust::min_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
int max_vertice_default_current_lag_variable(){
    //max in default stream
    thrust::device_ptr<int> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->current_lag);
    size_t result_offset = thrust::max_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
float reduce_vertice_default_min_variable(){
    //reduce in default stream
    return thrust::reduce(thrust::device_pointer_cast(d_vertices_default->min),  thrust::device_pointer_cast(d_vertices_default->min) + h_xmachine_memory_vertice_default_count);
}

float min_vertice_default_min_variable(){
    //min in default stream
    thrust::device_ptr<float> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->min);
    size_t result_offset = thrust::min_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
float max_vertice_default_min_variable(){
    //max in default stream
    thrust::device_ptr<float> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->min);
    size_t result_offset = thrust::max_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
float reduce_vertice_default_max_variable(){
    //reduce in default stream
    return thrust::reduce(thrust::device_pointer_cast(d_vertices_default->max),  thrust::device_pointer_cast(d_vertices_default->max) + h_xmachine_memory_vertice_default_count);
}

float min_vertice_default_max_variable(){
    //min in default stream
    thrust::device_ptr<float> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->max);
    size_t result_offset = thrust::min_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
float max_vertice_default_max_variable(){
    //max in default stream
    thrust::device_ptr<float> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->max);
    size_t result_offset = thrust::max_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
int reduce_vertice_default_need_test_variable(){
    //reduce in default stream
    return thrust::reduce(thrust::device_pointer_cast(d_vertices_default->need_test),  thrust::device_pointer_cast(d_vertices_default->need_test) + h_xmachine_memory_vertice_default_count);
}

int count_vertice_default_need_test_variable(int count_value){
    //count in default stream
    return (int)thrust::count(thrust::device_pointer_cast(d_vertices_default->need_test),  thrust::device_pointer_cast(d_vertices_default->need_test) + h_xmachine_memory_vertice_default_count, count_value);
}
int min_vertice_default_need_test_variable(){
    //min in default stream
    thrust::device_ptr<int> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->need_test);
    size_t result_offset = thrust::min_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
int max_vertice_default_need_test_variable(){
    //max in default stream
    thrust::device_ptr<int> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->need_test);
    size_t result_offset = thrust::max_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
int reduce_vertice_default_correct_variable(){
    //reduce in default stream
    return thrust::reduce(thrust::device_pointer_cast(d_vertices_default->correct),  thrust::device_pointer_cast(d_vertices_default->correct) + h_xmachine_memory_vertice_default_count);
}

int count_vertice_default_correct_variable(int count_value){
    //count in default stream
    return (int)thrust::count(thrust::device_pointer_cast(d_vertices_default->correct),  thrust::device_pointer_cast(d_vertices_default->correct) + h_xmachine_memory_vertice_default_count, count_value);
}
int min_vertice_default_correct_variable(){
    //min in default stream
    thrust::device_ptr<int> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->correct);
    size_t result_offset = thrust::min_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}
int max_vertice_default_correct_variable(){
    //max in default stream
    thrust::device_ptr<int> thrust_ptr = thrust::device_pointer_cast(d_vertices_default->correct);
    size_t result_offset = thrust::max_element(thrust_ptr, thrust_ptr + h_xmachine_memory_vertice_default_count) - thrust_ptr;
    return *(thrust_ptr + result_offset);
}



/* Agent functions */


	
/* Shared memory size calculator for agent function */
int vertice_send_message_sm_size(int blockSize){
	int sm_size;
	sm_size = SM_START;
  
	return sm_size;
}

/** vertice_send_message
 * Agent function prototype for send_message function of vertice agent
 */
void vertice_send_message(cudaStream_t &stream){

    int sm_size;
    int blockSize;
    int minGridSize;
    int gridSize;
    int state_list_size;
	dim3 g; //grid for agent func
	dim3 b; //block for agent func

	
	//CHECK THE CURRENT STATE LIST COUNT IS NOT EQUAL TO 0
	
	if (h_xmachine_memory_vertice_default_count == 0)
	{
		return;
	}
	
	
	//SET SM size to 0 and save state list size for occupancy calculations
	sm_size = SM_START;
	state_list_size = h_xmachine_memory_vertice_default_count;

	

	//******************************** AGENT FUNCTION CONDITION *********************
	//THERE IS NOT A FUNCTION CONDITION
	//currentState maps to working list
	xmachine_memory_vertice_list* vertices_default_temp = d_vertices;
	d_vertices = d_vertices_default;
	d_vertices_default = vertices_default_temp;
	//set working count to current state count
	h_xmachine_memory_vertice_count = h_xmachine_memory_vertice_default_count;
	gpuErrchk( cudaMemcpyToSymbol( d_xmachine_memory_vertice_count, &h_xmachine_memory_vertice_count, sizeof(int)));	
	//set current state count to 0
	h_xmachine_memory_vertice_default_count = 0;
	gpuErrchk( cudaMemcpyToSymbol( d_xmachine_memory_vertice_default_count, &h_xmachine_memory_vertice_default_count, sizeof(int)));	
	
 

	//******************************** AGENT FUNCTION *******************************

	
	//CONTINUOUS AGENT CHECK FUNCTION OUTPUT BUFFERS FOR OUT OF BOUNDS
	if (h_message_send_local_count + h_xmachine_memory_vertice_count > xmachine_message_send_local_MAX){
		printf("Error: Buffer size of send_local message will be exceeded in function send_message\n");
		exit(EXIT_FAILURE);
	}
	
	
	//calculate the grid block size for main agent function
	cudaOccupancyMaxPotentialBlockSizeVariableSMem( &minGridSize, &blockSize, GPUFLAME_send_message, vertice_send_message_sm_size, state_list_size);
	gridSize = (state_list_size + blockSize - 1) / blockSize;
	b.x = blockSize;
	g.x = gridSize;
	
	sm_size = vertice_send_message_sm_size(blockSize);
	
	
	
	//SET THE OUTPUT MESSAGE TYPE FOR CONTINUOUS AGENTS
	//Set the message_type for non partitioned, spatially partitioned and On-Graph Partitioned message outputs
	h_message_send_local_output_type = optional_message;
	gpuErrchk( cudaMemcpyToSymbol( d_message_send_local_output_type, &h_message_send_local_output_type, sizeof(int)));
	//message is optional so reset the swap
	cudaOccupancyMaxPotentialBlockSizeVariableSMem( &minGridSize, &blockSize, reset_send_local_swaps, no_sm, state_list_size); 
	gridSize = (state_list_size + blockSize - 1) / blockSize;
	reset_send_local_swaps<<<gridSize, blockSize, 0, stream>>>(d_send_locals); 
	gpuErrchkLaunch();
	
	
	//MAIN XMACHINE FUNCTION CALL (send_message)
	//Reallocate   : false
	//Input        : 
	//Output       : send_local
	//Agent Output : 
	GPUFLAME_send_message<<<g, b, sm_size, stream>>>(d_vertices, d_send_locals, d_rand48);
	gpuErrchkLaunch();
	
	
	//CONTINUOUS AGENTS SCATTER NON PARTITIONED OPTIONAL OUTPUT MESSAGES
	//send_local Message Type Prefix Sum
	
	//swap output
	xmachine_message_send_local_list* d_send_locals_scanswap_temp = d_send_locals;
	d_send_locals = d_send_locals_swap;
	d_send_locals_swap = d_send_locals_scanswap_temp;
	
    cub::DeviceScan::ExclusiveSum(
        d_temp_scan_storage_vertice, 
        temp_scan_storage_bytes_vertice, 
        d_send_locals_swap->_scan_input,
        d_send_locals_swap->_position,
        h_xmachine_memory_vertice_count, 
        stream
    );

	//Scatter
	cudaOccupancyMaxPotentialBlockSizeVariableSMem( &minGridSize, &blockSize, scatter_optional_send_local_messages, no_sm, state_list_size); 
	gridSize = (state_list_size + blockSize - 1) / blockSize;
	scatter_optional_send_local_messages<<<gridSize, blockSize, 0, stream>>>(d_send_locals, d_send_locals_swap);
	gpuErrchkLaunch();
	
	//UPDATE MESSAGE COUNTS FOR CONTINUOUS AGENTS WITH NON PARTITIONED MESSAGE OUTPUT 
	gpuErrchk( cudaMemcpy( &scan_last_sum, &d_send_locals_swap->_position[h_xmachine_memory_vertice_count-1], sizeof(int), cudaMemcpyDeviceToHost));
	gpuErrchk( cudaMemcpy( &scan_last_included, &d_send_locals_swap->_scan_input[h_xmachine_memory_vertice_count-1], sizeof(int), cudaMemcpyDeviceToHost));
	//If last item in prefix sum was 1 then increase its index to get the count
	if (scan_last_included == 1){
		h_message_send_local_count += scan_last_sum+1;
	}else{
		h_message_send_local_count += scan_last_sum;
	}
    //Copy count to device
	gpuErrchk( cudaMemcpyToSymbol( d_message_send_local_count, &h_message_send_local_count, sizeof(int)));	
	
	
	//************************ MOVE AGENTS TO NEXT STATE ****************************
    
	//check the working agents wont exceed the buffer size in the new state list
	if (h_xmachine_memory_vertice_default_count+h_xmachine_memory_vertice_count > xmachine_memory_vertice_MAX){
		printf("Error: Buffer size of send_message agents in state default will be exceeded moving working agents to next state in function send_message\n");
      exit(EXIT_FAILURE);
      }
      
  //pointer swap the updated data
  vertices_default_temp = d_vertices;
  d_vertices = d_vertices_default;
  d_vertices_default = vertices_default_temp;
        
	//update new state agent size
	h_xmachine_memory_vertice_default_count += h_xmachine_memory_vertice_count;
	gpuErrchk( cudaMemcpyToSymbol( d_xmachine_memory_vertice_default_count, &h_xmachine_memory_vertice_default_count, sizeof(int)));	
	
	
}



	
/* Shared memory size calculator for agent function */
int vertice_read_message_sm_size(int blockSize){
	int sm_size;
	sm_size = SM_START;
  //Continuous agent and message input has no partitioning
	sm_size += (blockSize * sizeof(xmachine_message_send_local));
	
	//all continuous agent types require single 32bit word per thread offset (to avoid sm bank conflicts)
	sm_size += (blockSize * PADDING);
	
	return sm_size;
}

/** vertice_read_message
 * Agent function prototype for read_message function of vertice agent
 */
void vertice_read_message(cudaStream_t &stream){

    int sm_size;
    int blockSize;
    int minGridSize;
    int gridSize;
    int state_list_size;
	dim3 g; //grid for agent func
	dim3 b; //block for agent func

	
	//CHECK THE CURRENT STATE LIST COUNT IS NOT EQUAL TO 0
	
	if (h_xmachine_memory_vertice_default_count == 0)
	{
		return;
	}
	
	
	//SET SM size to 0 and save state list size for occupancy calculations
	sm_size = SM_START;
	state_list_size = h_xmachine_memory_vertice_default_count;

	

	//******************************** AGENT FUNCTION CONDITION *********************
	//THERE IS NOT A FUNCTION CONDITION
	//currentState maps to working list
	xmachine_memory_vertice_list* vertices_default_temp = d_vertices;
	d_vertices = d_vertices_default;
	d_vertices_default = vertices_default_temp;
	//set working count to current state count
	h_xmachine_memory_vertice_count = h_xmachine_memory_vertice_default_count;
	gpuErrchk( cudaMemcpyToSymbol( d_xmachine_memory_vertice_count, &h_xmachine_memory_vertice_count, sizeof(int)));	
	//set current state count to 0
	h_xmachine_memory_vertice_default_count = 0;
	gpuErrchk( cudaMemcpyToSymbol( d_xmachine_memory_vertice_default_count, &h_xmachine_memory_vertice_default_count, sizeof(int)));	
	
 

	//******************************** AGENT FUNCTION *******************************

	
	
	//calculate the grid block size for main agent function
	cudaOccupancyMaxPotentialBlockSizeVariableSMem( &minGridSize, &blockSize, GPUFLAME_read_message, vertice_read_message_sm_size, state_list_size);
	gridSize = (state_list_size + blockSize - 1) / blockSize;
	b.x = blockSize;
	g.x = gridSize;
	
	sm_size = vertice_read_message_sm_size(blockSize);
	
	
	
	//BIND APPROPRIATE MESSAGE INPUT VARIABLES TO TEXTURES (to make use of the texture cache)
	
	
	//MAIN XMACHINE FUNCTION CALL (read_message)
	//Reallocate   : false
	//Input        : send_local
	//Output       : 
	//Agent Output : 
	GPUFLAME_read_message<<<g, b, sm_size, stream>>>(d_vertices, d_send_locals, d_rand48);
	gpuErrchkLaunch();
	
	
	//UNBIND MESSAGE INPUT VARIABLE TEXTURES
	
	
	//************************ MOVE AGENTS TO NEXT STATE ****************************
    
	//check the working agents wont exceed the buffer size in the new state list
	if (h_xmachine_memory_vertice_default_count+h_xmachine_memory_vertice_count > xmachine_memory_vertice_MAX){
		printf("Error: Buffer size of read_message agents in state default will be exceeded moving working agents to next state in function read_message\n");
      exit(EXIT_FAILURE);
      }
      
  //pointer swap the updated data
  vertices_default_temp = d_vertices;
  d_vertices = d_vertices_default;
  d_vertices_default = vertices_default_temp;
        
	//update new state agent size
	h_xmachine_memory_vertice_default_count += h_xmachine_memory_vertice_count;
	gpuErrchk( cudaMemcpyToSymbol( d_xmachine_memory_vertice_default_count, &h_xmachine_memory_vertice_default_count, sizeof(int)));	
	
	
}


 
extern void reset_vertice_default_count()
{
    h_xmachine_memory_vertice_default_count = 0;
}
