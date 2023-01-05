
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


#include <cuda_runtime.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <cmath>
#include <limits.h>
#include <algorithm>
#include <string>
#include <vector>



#ifdef _WIN32
#define strtok_r strtok_s
#endif

// include header
#include "header.h"

glm::vec3 agent_maximum;
glm::vec3 agent_minimum;

int fpgu_strtol(const char* str){
    return (int)strtol(str, NULL, 0);
}

unsigned int fpgu_strtoul(const char* str){
    return (unsigned int)strtoul(str, NULL, 0);
}

long long int fpgu_strtoll(const char* str){
    return strtoll(str, NULL, 0);
}

unsigned long long int fpgu_strtoull(const char* str){
    return strtoull(str, NULL, 0);
}

double fpgu_strtod(const char* str){
    return strtod(str, NULL);
}

float fgpu_atof(const char* str){
    return (float)atof(str);
}


//templated class function to read array inputs from supported types
template <class T>
void readArrayInput( T (*parseFunc)(const char*), char* buffer, T *array, unsigned int expected_items, const char * agent_name, const char * variable_name){
    unsigned int i = 0;
    const char s[2] = ",";
    char * token;
    char * end_str;

    token = strtok_r(buffer, s, &end_str);
    while (token != NULL){
        if (i>=expected_items){
            fprintf(stderr, "Error: variable array %s->%s has too many items (%d), expected %d!\n", agent_name, variable_name, i, expected_items);
            exit(EXIT_FAILURE);
        }
        
        array[i++] = (T)parseFunc(token);
        
        token = strtok_r(NULL, s, &end_str);
    }
    #if ! defined(SUPPRESS_VARIABLE_ARRAY_ELEMENT_WARNING)
    if (i != expected_items){
        fprintf(stderr, "Warning: variable array %s->%s has %d items, expected %d!\n", agent_name, variable_name, i, expected_items);
        
    }
    #endif
}

//templated class function to read array inputs from supported types
template <class T, class BASE_T, unsigned int D>
void readArrayInputVectorType( BASE_T (*parseFunc)(const char*), char* buffer, T *array, unsigned int expected_items, const char * agent_name, const char * variable_name){
    unsigned int i = 0;
    const char s[2] = "|";
    char * token;
    char * end_str;

    token = strtok_r(buffer, s, &end_str);
    while (token != NULL){
        if (i>=expected_items){
            fprintf(stderr, "Error: variable array of vectors %s->%s has too many items (%d), expected %d!\n", agent_name, variable_name, i, expected_items);
        }
        
        //read vector type as an array
        T vec;
        readArrayInput<BASE_T>(parseFunc, token, (BASE_T*) &vec, D);
        array[i++] = vec;
        
        token = strtok_r(NULL, s, &end_str);
    }
    #if ! defined(SUPPRESS_VARIABLE_ARRAY_ELEMENT_WARNING)
    if (i != expected_items){
        fprintf(stderr, "Warning: variable array of vectors %s->%s has %d items, expected %d!\n", agent_name, variable_name, i, expected_items);
        
    }
    #endif
}

void saveIterationData(char* outputpath, int iteration_number, xmachine_memory_vertice_list* h_vertices_default, xmachine_memory_vertice_list* d_vertices_default, int h_xmachine_memory_vertice_default_count)
{
    PROFILE_SCOPED_RANGE("saveIterationData");
	cudaError_t cudaStatus;
	
	//Device to host memory transfer
	
	cudaStatus = cudaMemcpy( h_vertices_default, d_vertices_default, sizeof(xmachine_memory_vertice_list), cudaMemcpyDeviceToHost);
	if (cudaStatus != cudaSuccess)
	{
		fprintf(stderr,"Error Copying vertice Agent default State Memory from GPU: %s\n", cudaGetErrorString(cudaStatus));
		exit(cudaStatus);
	}
	
	/* Pointer to file */
	FILE *file;
	char data[100];

	sprintf(data, "%s%i.xml", outputpath, iteration_number);
	//printf("Writing iteration %i data to %s\n", iteration_number, data);
	file = fopen(data, "w");
    if(file == nullptr){
        printf("Error: Could not open file `%s` for output. Aborting.\n", data);
        exit(EXIT_FAILURE);
    }
    fputs("<states>\n<itno>", file);
    sprintf(data, "%i", iteration_number);
    fputs(data, file);
    fputs("</itno>\n", file);
    fputs("<environment>\n" , file);
    
    fputs("\t<VERTICES_COUNT>", file);
    sprintf(data, "%d", (*get_VERTICES_COUNT()));
    fputs(data, file);
    fputs("</VERTICES_COUNT>\n", file);
	fputs("</environment>\n" , file);

	//Write each vertice agent to xml
	for (int i=0; i<h_xmachine_memory_vertice_default_count; i++){
		fputs("<xagent>\n" , file);
		fputs("<name>vertice</name>\n", file);
        
		fputs("<id>", file);
        sprintf(data, "%d", h_vertices_default->id[i]);
		fputs(data, file);
		fputs("</id>\n", file);
        
		fputs("<value>", file);
        sprintf(data, "%f", h_vertices_default->value[i]);
		fputs(data, file);
		fputs("</value>\n", file);
        
		fputs("<add_value>", file);
        sprintf(data, "%f", h_vertices_default->add_value[i]);
		fputs(data, file);
		fputs("</add_value>\n", file);
        
		fputs("<previous>", file);
        sprintf(data, "%f", h_vertices_default->previous[i]);
		fputs(data, file);
		fputs("</previous>\n", file);
        
		fputs("<max_lag>", file);
        sprintf(data, "%d", h_vertices_default->max_lag[i]);
		fputs(data, file);
		fputs("</max_lag>\n", file);
        
		fputs("<current_lag>", file);
        sprintf(data, "%d", h_vertices_default->current_lag[i]);
		fputs(data, file);
		fputs("</current_lag>\n", file);
        
		fputs("<edges>", file);
        for (int j=0;j<17;j++){
            fprintf(file, "%f", h_vertices_default->edges[(j*xmachine_memory_vertice_MAX)+i]);
            if(j!=(17-1))
                fprintf(file, ",");
        }
		fputs("</edges>\n", file);
        
		fputs("<min>", file);
        sprintf(data, "%f", h_vertices_default->min[i]);
		fputs(data, file);
		fputs("</min>\n", file);
        
		fputs("<max>", file);
        sprintf(data, "%f", h_vertices_default->max[i]);
		fputs(data, file);
		fputs("</max>\n", file);
        
		fputs("<need_test>", file);
        sprintf(data, "%d", h_vertices_default->need_test[i]);
		fputs(data, file);
		fputs("</need_test>\n", file);
        
		fputs("<correct>", file);
        sprintf(data, "%d", h_vertices_default->correct[i]);
		fputs(data, file);
		fputs("</correct>\n", file);
        
		fputs("</xagent>\n", file);
	}
	
	

	fputs("</states>\n" , file);
	
	/* Close the file */
	fclose(file);

}

void initEnvVars()
{
PROFILE_SCOPED_RANGE("initEnvVars");

    int t_VERTICES_COUNT = (int)17;
    set_VERTICES_COUNT(&t_VERTICES_COUNT);
}

void readInitialStates(char* inputpath, xmachine_memory_vertice_list* h_vertices, int* h_xmachine_memory_vertice_count)
{
    PROFILE_SCOPED_RANGE("readInitialStates");

	int temp = 0;
	int* itno = &temp;

	/* Pointer to file */
	FILE *file;
	/* Char and char buffer for reading file to */
	char c = ' ';
	const int bufferSize = 10000;
	char buffer[bufferSize];
	char agentname[1000];

	/* Pointer to x-memory for initial state data */
	/*xmachine * current_xmachine;*/
	/* Variables for checking tags */
	int reading, i;
	int in_tag, in_itno, in_xagent, in_name, in_comment;
    int in_vertice_id;
    int in_vertice_value;
    int in_vertice_add_value;
    int in_vertice_previous;
    int in_vertice_max_lag;
    int in_vertice_current_lag;
    int in_vertice_edges;
    int in_vertice_min;
    int in_vertice_max;
    int in_vertice_need_test;
    int in_vertice_correct;
    
    /* tags for environment global variables */
    int in_env;
    int in_env_VERTICES_COUNT;
    
	/* set agent count to zero */
	*h_xmachine_memory_vertice_count = 0;
	
	/* Variables for initial state data */
	int vertice_id;
	float vertice_value;
	float vertice_add_value;
	float vertice_previous;
	int vertice_max_lag;
	int vertice_current_lag;
    float vertice_edges[17];
	float vertice_min;
	float vertice_max;
	int vertice_need_test;
	int vertice_correct;

    /* Variables for environment variables */
    int env_VERTICES_COUNT;
    


	/* Initialise variables */
    initEnvVars();
    agent_maximum.x = 0;
    agent_maximum.y = 0;
    agent_maximum.z = 0;
    agent_minimum.x = 0;
    agent_minimum.y = 0;
    agent_minimum.z = 0;
	reading = 1;
    in_comment = 0;
	in_tag = 0;
	in_itno = 0;
    in_env = 0;
    in_xagent = 0;
	in_name = 0;
	in_vertice_id = 0;
	in_vertice_value = 0;
	in_vertice_add_value = 0;
	in_vertice_previous = 0;
	in_vertice_max_lag = 0;
	in_vertice_current_lag = 0;
	in_vertice_edges = 0;
	in_vertice_min = 0;
	in_vertice_max = 0;
	in_vertice_need_test = 0;
	in_vertice_correct = 0;
    in_env_VERTICES_COUNT = 0;
	//set all vertice values to 0
	//If this is not done then it will cause errors in emu mode where undefined memory is not 0
	for (int k=0; k<xmachine_memory_vertice_MAX; k++)
	{	
		h_vertices->id[k] = 0;
		h_vertices->value[k] = 0;
		h_vertices->add_value[k] = 0;
		h_vertices->previous[k] = 0;
		h_vertices->max_lag[k] = 0;
		h_vertices->current_lag[k] = 0;
        for (i=0;i<17;i++){
            h_vertices->edges[(i*xmachine_memory_vertice_MAX)+k] = 0;
        }
		h_vertices->min[k] = 0;
		h_vertices->max[k] = 0;
		h_vertices->need_test[k] = 0;
		h_vertices->correct[k] = 0;
	}
	

	/* Default variables for memory */
    vertice_id = 0;
    vertice_value = 0;
    vertice_add_value = 0;
    vertice_previous = 0;
    vertice_max_lag = 0;
    vertice_current_lag = 0;
    for (i=0;i<17;i++){
        vertice_edges[i] = 0;
    }
    vertice_min = 0;
    vertice_max = 0;
    vertice_need_test = 0;
    vertice_correct = 0;

    /* Default variables for environment variables */
    env_VERTICES_COUNT = 17;
    


    // Declare and initialise variables tracking the maximum agent id for each agent type from the initial population
    int max_vertice_id = 0;
    
    
    // If no input path was specified, issue a message and return.
    if(inputpath[0] == '\0'){
        printf("No initial states file specified. Using default values.\n");
        return;
    }
    
    // Otherwise an input path was specified, and we have previously checked that it is (was) not a directory. 
    
	// Attempt to open the non directory path as read only.
	file = fopen(inputpath, "r");
    
    // If the file could not be opened, issue a message and return.
    if(file == nullptr)
    {
      printf("Could not open input file %s. Continuing with default values\n", inputpath);
      return;
    }
    // Otherwise we can iterate the file until the end of XML is reached.
    size_t bytesRead = 0;
    i = 0;
	while(reading==1)
	{
        // If I exceeds our buffer size we must abort
        if(i >= bufferSize){
            fprintf(stderr, "Error: XML Parsing failed Tag name or content too long (> %d characters)\n", bufferSize);
            exit(EXIT_FAILURE);
        }

		/* Get the next char from the file */
		c = (char)fgetc(file);

        // Check if we reached the end of the file.
        if(c == EOF){
            // Break out of the loop. This allows for empty files(which may or may not be)
            break;
        }
        // Increment byte counter.
        bytesRead++;

        /*If in a  comment, look for the end of a comment */
        if(in_comment){

            /* Look for an end tag following two (or more) hyphens.
               To support very long comments, we use the minimal amount of buffer we can. 
               If we see a hyphen, store it and increment i (but don't increment i)
               If we see a > check if we have a correct terminating comment
               If we see any other characters, reset i.
            */

            if(c == '-'){
                buffer[i] = c;
                i++;
            } else if(c == '>' && i >= 2){
                in_comment = 0;
                i = 0;
            } else {
                i = 0;
            }

            /*// If we see the end tag, check the preceding two characters for a close comment, if enough characters have been read for -->
            if(c == '>' && i >= 2 && buffer[i-1] == '-' && buffer[i-2] == '-'){
                in_comment = 0;
                buffer[0] = 0;
                i = 0;
            } else {
                // Otherwise just store it in the buffer so we can keep checking for close tags
                buffer[i] = c;
                i++;
            }*/
        }
		/* If the end of a tag */
		else if(c == '>')
		{
			/* Place 0 at end of buffer to make chars a string */
			buffer[i] = 0;

			if(strcmp(buffer, "states") == 0) reading = 1;
			if(strcmp(buffer, "/states") == 0) reading = 0;
			if(strcmp(buffer, "itno") == 0) in_itno = 1;
			if(strcmp(buffer, "/itno") == 0) in_itno = 0;
            if(strcmp(buffer, "environment") == 0) in_env = 1;
            if(strcmp(buffer, "/environment") == 0) in_env = 0;
			if(strcmp(buffer, "name") == 0) in_name = 1;
			if(strcmp(buffer, "/name") == 0) in_name = 0;
            if(strcmp(buffer, "xagent") == 0) in_xagent = 1;
			if(strcmp(buffer, "/xagent") == 0)
			{
				if(strcmp(agentname, "vertice") == 0)
				{
					if (*h_xmachine_memory_vertice_count > xmachine_memory_vertice_MAX){
						printf("ERROR: MAX Buffer size (%i) for agent vertice exceeded whilst reading data\n", xmachine_memory_vertice_MAX);
						// Close the file and stop reading
						fclose(file);
						exit(EXIT_FAILURE);
					}
                    
					h_vertices->id[*h_xmachine_memory_vertice_count] = vertice_id;
					h_vertices->value[*h_xmachine_memory_vertice_count] = vertice_value;
					h_vertices->add_value[*h_xmachine_memory_vertice_count] = vertice_add_value;
					h_vertices->previous[*h_xmachine_memory_vertice_count] = vertice_previous;
					h_vertices->max_lag[*h_xmachine_memory_vertice_count] = vertice_max_lag;
					h_vertices->current_lag[*h_xmachine_memory_vertice_count] = vertice_current_lag;
                    for (int k=0;k<17;k++){
                        h_vertices->edges[(k*xmachine_memory_vertice_MAX)+(*h_xmachine_memory_vertice_count)] = vertice_edges[k];
                    }
					h_vertices->min[*h_xmachine_memory_vertice_count] = vertice_min;
					h_vertices->max[*h_xmachine_memory_vertice_count] = vertice_max;
					h_vertices->need_test[*h_xmachine_memory_vertice_count] = vertice_need_test;
					h_vertices->correct[*h_xmachine_memory_vertice_count] = vertice_correct;
					(*h_xmachine_memory_vertice_count) ++;	
				}
				else
				{
					printf("Warning: agent name undefined - '%s'\n", agentname);
				}



				/* Reset xagent variables */
                vertice_id = 0;
                vertice_value = 0;
                vertice_add_value = 0;
                vertice_previous = 0;
                vertice_max_lag = 0;
                vertice_current_lag = 0;
                for (i=0;i<17;i++){
                    vertice_edges[i] = 0;
                }
                vertice_min = 0;
                vertice_max = 0;
                vertice_need_test = 0;
                vertice_correct = 0;
                
                in_xagent = 0;
			}
			if(strcmp(buffer, "id") == 0) in_vertice_id = 1;
			if(strcmp(buffer, "/id") == 0) in_vertice_id = 0;
			if(strcmp(buffer, "value") == 0) in_vertice_value = 1;
			if(strcmp(buffer, "/value") == 0) in_vertice_value = 0;
			if(strcmp(buffer, "add_value") == 0) in_vertice_add_value = 1;
			if(strcmp(buffer, "/add_value") == 0) in_vertice_add_value = 0;
			if(strcmp(buffer, "previous") == 0) in_vertice_previous = 1;
			if(strcmp(buffer, "/previous") == 0) in_vertice_previous = 0;
			if(strcmp(buffer, "max_lag") == 0) in_vertice_max_lag = 1;
			if(strcmp(buffer, "/max_lag") == 0) in_vertice_max_lag = 0;
			if(strcmp(buffer, "current_lag") == 0) in_vertice_current_lag = 1;
			if(strcmp(buffer, "/current_lag") == 0) in_vertice_current_lag = 0;
			if(strcmp(buffer, "edges") == 0) in_vertice_edges = 1;
			if(strcmp(buffer, "/edges") == 0) in_vertice_edges = 0;
			if(strcmp(buffer, "min") == 0) in_vertice_min = 1;
			if(strcmp(buffer, "/min") == 0) in_vertice_min = 0;
			if(strcmp(buffer, "max") == 0) in_vertice_max = 1;
			if(strcmp(buffer, "/max") == 0) in_vertice_max = 0;
			if(strcmp(buffer, "need_test") == 0) in_vertice_need_test = 1;
			if(strcmp(buffer, "/need_test") == 0) in_vertice_need_test = 0;
			if(strcmp(buffer, "correct") == 0) in_vertice_correct = 1;
			if(strcmp(buffer, "/correct") == 0) in_vertice_correct = 0;
			
            /* environment variables */
            if(strcmp(buffer, "VERTICES_COUNT") == 0) in_env_VERTICES_COUNT = 1;
            if(strcmp(buffer, "/VERTICES_COUNT") == 0) in_env_VERTICES_COUNT = 0;
			

			/* End of tag and reset buffer */
			in_tag = 0;
			i = 0;
		}
		/* If start of tag */
		else if(c == '<')
		{
			/* Place /0 at end of buffer to end numbers */
			buffer[i] = 0;
			/* Flag in tag */
			in_tag = 1;

			if(in_itno) *itno = atoi(buffer);
			if(in_name) strcpy(agentname, buffer);
			else if (in_xagent)
			{
				if(in_vertice_id){
                    vertice_id = (int) fpgu_strtol(buffer); 
                    if(vertice_id > max_vertice_id){
                        max_vertice_id = vertice_id;
                    }
                    
                }
				if(in_vertice_value){
                    vertice_value = (float) fgpu_atof(buffer); 
                }
				if(in_vertice_add_value){
                    vertice_add_value = (float) fgpu_atof(buffer); 
                }
				if(in_vertice_previous){
                    vertice_previous = (float) fgpu_atof(buffer); 
                }
				if(in_vertice_max_lag){
                    vertice_max_lag = (int) fpgu_strtol(buffer); 
                }
				if(in_vertice_current_lag){
                    vertice_current_lag = (int) fpgu_strtol(buffer); 
                }
				if(in_vertice_edges){
                    readArrayInput<float>(&fgpu_atof, buffer, vertice_edges, 17, "vertice", "edges");    
                }
				if(in_vertice_min){
                    vertice_min = (float) fgpu_atof(buffer); 
                }
				if(in_vertice_max){
                    vertice_max = (float) fgpu_atof(buffer); 
                }
				if(in_vertice_need_test){
                    vertice_need_test = (int) fpgu_strtol(buffer); 
                }
				if(in_vertice_correct){
                    vertice_correct = (int) fpgu_strtol(buffer); 
                }
				
            }
            else if (in_env){
            if(in_env_VERTICES_COUNT){
              
                    env_VERTICES_COUNT = (int) fpgu_strtol(buffer);
                    
                    set_VERTICES_COUNT(&env_VERTICES_COUNT);
                  
              }
            
            }
		/* Reset buffer */
			i = 0;
		}
		/* If in tag put read char into buffer */
		else if(in_tag)
		{
            // Check if we are a comment, when we are in a tag and buffer[0:2] == "!--"
            if(i == 2 && c == '-' && buffer[1] == '-' && buffer[0] == '!'){
                in_comment = 1;
                // Reset the buffer and i.
                buffer[0] = 0;
                i = 0;
            }

            // Store the character and increment the counter
            buffer[i] = c;
            i++;

		}
		/* If in data read char into buffer */
		else
		{
			buffer[i] = c;
			i++;
		}
	}
    // If no bytes were read, raise a warning.
    if(bytesRead == 0){
        fprintf(stdout, "Warning: %s is an empty file\n", inputpath);
        fflush(stdout);
    }

    // If the in_comment flag is still marked, issue a warning.
    if(in_comment){
        fprintf(stdout, "Warning: Un-terminated comment in %s\n", inputpath);
        fflush(stdout);
    }    

	/* Close the file */
	fclose(file);

    // IF required, set the first id value to maximum plus one.
    
    // If any agents of this type were found, use the maximum value +1
    if(h_xmachine_memory_vertice_count > 0){
        set_initial_vertice_id(max_vertice_id + 1);

    } else {
    // Otherwise use 0.
        set_initial_vertice_id(0);
    }


    
}

glm::vec3 getMaximumBounds(){
    return agent_maximum;
}

glm::vec3 getMinimumBounds(){
    return agent_minimum;
}


/* Methods to load static networks from disk */
