
#ifndef _FLAMEGPU_FUNCTIONS
#define _FLAMEGPU_FUNCTIONS

#include <header.h>

__FLAME_GPU_FUNC__ int send_message(xmachine_memory_vertice* agent, xmachine_message_send_local_list* data_messages, RNG_rand48* rand48){


    float value = agent->value - agent->previous;
    if (value > 0.0001 || value < -0.0001 ){
	add_send_local_message(data_messages, agent->id, value);
    }
    return 0;
}

__FLAME_GPU_FUNC__ int read_message(xmachine_memory_vertice* agent, xmachine_message_send_local_list* data_messages, RNG_rand48* rand48){

    xmachine_message_send_local* current_message = get_first_send_local_message(data_messages);
    
    int edge_value = 0;

    agent->previous = agent->value;

    float temp_value = 0;

    while(current_message){

	for (int i = 0; i < VERTICES_COUNT; i++){
	    edge_value = get_vertice_agent_array_value<int>(agent->edges, i);
	    if ((current_message->from_id == i) && (edge_value != 0)){
		//agent->value = agent->value + current_message->value * edge_value;
		temp_value = temp_value + current_message->value * edge_value;
	    }
	}

	current_message = get_next_send_local_message(current_message, data_messages);
    }

    // calculate agent value
    if (temp_value > 0.0001 || temp_value < -0.0001){
	agent->add_value = ((agent->current_lag * agent->add_value) + temp_value) / agent->max_lag;
	agent->current_lag = agent->max_lag;
    }

    if (agent->current_lag > 0){
	agent->value = agent->value + agent->add_value;
	agent->current_lag = agent->current_lag - 1;
    }

    return 0;
}


#endif //_FLAMEGPU_FUNCTIONS

