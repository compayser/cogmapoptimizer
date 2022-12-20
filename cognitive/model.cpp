#include "stdio.h"
#include "model.h"

#include <malloc.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>

#include <sys/stat.h>

#include <iostream>
#include <fstream>

#include "string.h"

#define FILES_COUNT 5

std::string files_list[FILES_COUNT] = {"/Makefile", "/make.sh", "/run.sh", "/src/model/XMLModelFile.xml", "/src/model/functions.c"};

TModel* TModel::p_instance = 0;

TModel::TModel()
{
    rawJSON = NULL;
    json = NULL;

    char * line = NULL;
    size_t len  = 0;
    ssize_t read;

    FILE * fp = fopen("config.txt", "r");
    if (fp == NULL){
	printf("Error! Can't load configuration file. Set default value.\n");

	data.name = "cognitiv-task";
	data.visual = 0;
	data.path = "/home/user/Projects/Ivan/flame/FLAMEGPU-master/";
	data.iterPath = "/home/user/Projects/Ivan/flame/FLAMEGPU-master/projects/" + data.name + "/iterations/";
	data.iterCount = 5;
	return;
    }


    if ( (read = getline(&line, &len, fp) ) != -1) {
        line[strlen(line) - 1] = '\0';
	data.name = line;
    }

    printf("data.name=[%s]\n", data.name.c_str());

    if ( (read = getline(&line, &len, fp) ) != -1)
	data.visual = atoi(line);

    if ( (read = getline(&line, &len, fp) ) != -1){
	line[strlen(line) - 1] = '\0';
	data.path = line;
    }

    printf("data.path=[%s]\n", data.path.c_str());

    if ( (read = getline(&line, &len, fp) ) != -1){
	line[strlen(line) - 1] = '\0';
	data.iterPath = line + data.name + "/iterations/";
    }

    printf("data.iterPath=[%s]\n", data.iterPath.c_str());

    if ( (read = getline(&line, &len, fp) ) != -1)
	data.iterCount = atoi(line);

    fclose(fp);

    fp = fopen("impulse-lag.txt", "r");
    if (fp == NULL){
	printf("Error! Can't load configuration impulse lags file\n");
	return;

    }

    while( (read = getline(&line, &len, fp) ) != -1 ){
	data.lags.push_back(atoi(line));
    }

    if (line) free(line);

}


TModel::~TModel()
{
    if (rawJSON) free(rawJSON);
    if (json) nx_json_free(json);
}

bool TModel::set_vert(std::vector<TEdge> &e,std::vector<TVertice> v)
{
    for (std::vector<TEdge>::iterator e_iter = e.begin(); e_iter != e.end(); e_iter++){
	e_iter->v1_id = -1;
	e_iter->v2_id = -1;
	unsigned int id = 0;
	for(std::vector<TVertice>::iterator v_iter = v.begin(); v_iter != v.end(); v_iter++){
		if (e_iter->v1 == v_iter->id) e_iter->v1_id = id;
		if (e_iter->v2 == v_iter->id) e_iter->v2_id = id;
		id++;
	}
	if (e_iter->v1_id == -1) {
	    printf("Cant find vertice (v1) for edge id=%ld\n", e_iter->v1);
	    return false;
	}
	if (e_iter->v2_id == -1) {
	    printf("Cant find vertice (v2) for edge id=%ld\n", e_iter->v2);
	    return false;
	}
    }
    return true;
}


int  TModel::get_weight(int id, int to_id){

	for (int i_edges = 0; i_edges < data.edges.size(); i_edges++){
		if ( data.edges[i_edges].v1_id == id && data.edges[i_edges].v2_id == to_id )
		    return data.edges[i_edges].weight;
	}
	return 0;
}

void TModel::initFromJSON()
{



    const nx_json * retData;
    const nx_json * retArrayData;
    const nx_json * retData_2;

    retData = nx_json_get(json, "Vertices");
    retArrayData = retData->child;
    while (retArrayData != NULL) {
// {"color":"0x808080ff","show":"false","x":144.0,"fullName":"К1","y":64.0,"growth":0.0,"id":1655712545685,"shortName":"V1","value":0.0},
	TVertice tmp_vert;

	//"fullName":"К1"
	retData_2 = nx_json_get(retArrayData, "fullName");
	printf("Vertice name: [%s]\n", retData_2->text_value);
	tmp_vert.name = retData_2->text_value;

	//"id":1655712545685
	retData_2 = nx_json_get(retArrayData, "id");
	printf("Vertice ID: [%ld]\n", retData_2->int_value);
	tmp_vert.id = retData_2->int_value;

	retData_2 = nx_json_get(retArrayData, "value");
	printf("Vertice value: [%f]\n", retData_2->dbl_value);
	tmp_vert.value = retData_2->dbl_value;

	data.vertices.push_back(tmp_vert);
	printf("\n");

	retArrayData = retArrayData->next;
    }

    retData = nx_json_get(json, "Edges");
    retArrayData = retData->child;
    while (retArrayData != NULL) {
// {"color":"0x808080ff","md":"(207.0,65.0)","weight":1.0,"formula":"","id":1655712630647,"v1":1655712545685,"shortName":"","v2":1655712594662},
	TEdge	tmp_edge;

	retData_2 = nx_json_get(retArrayData, "shortName");
	printf("Edge shortName: [%s]\n", retData_2->text_value);
	tmp_edge.name = retData_2->text_value;

	retData_2 = nx_json_get(retArrayData, "formula");
	printf("Edge formula: [%s]\n", retData_2->text_value);
	tmp_edge.formula = retData_2->text_value;

	retData_2 = nx_json_get(retArrayData, "id");
	printf("Edge ID: [%ld]\n", retData_2->int_value);
	tmp_edge.id = retData_2->int_value;

	retData_2 = nx_json_get(retArrayData, "v1");
	printf("Edge ID V1: [%ld]\n", retData_2->int_value);
	tmp_edge.v1 = retData_2->int_value;

	retData_2 = nx_json_get(retArrayData, "v2");
	printf("Edge ID V2: [%ld]\n", retData_2->int_value);
	tmp_edge.v2 = retData_2->int_value;

	retData_2 = nx_json_get(retArrayData, "weight");
	printf("Edge weight: [%f]\n", retData_2->dbl_value);
	tmp_edge.weight = retData_2->dbl_value;

	data.edges.push_back(tmp_edge);
	printf("\n");

	retArrayData = retArrayData->next;
    }

    const nx_json * beforeData, * beforeDataArray;

    beforeData = nx_json_get(json, "Scenarios");
    beforeDataArray = beforeData->child;
    while(beforeDataArray != NULL) {

        retData = nx_json_get(beforeDataArray, "impulses");
        retArrayData = retData->child;
        while (retArrayData != NULL) {
    // "impulses":[{"val":1.0,"v":1655712545685,"step":0},{"val":-1.0,"v":1655712594662,"step":1},{"val":-1.0,"v":1655712747678,"step":1}],
		TImpulse	tmp_impulse;

		retData_2 = nx_json_get(retArrayData, "v");
		printf("Impulse ID: [%ld]\n", retData_2->int_value);
		tmp_impulse.v = retData_2->int_value;

		retData_2 = nx_json_get(retArrayData, "step");
		printf("Impulse step: [%ld]\n", retData_2->int_value);
		tmp_impulse.step = retData_2->int_value;
    
		retData_2 = nx_json_get(retArrayData, "val");
		printf("Impulse val: [%f]\n", retData_2->dbl_value);
		tmp_impulse.value = retData_2->dbl_value;

		data.impulses.push_back(tmp_impulse);
		printf("\n");

		retArrayData = retArrayData->next;
	}// while (retArrayData != NULL) {

	beforeDataArray = beforeDataArray->next;
    }// while(beforeDataArray != NULL) {


    set_vert(data.edges, data.vertices);
}

bool TModel::loadFromJSON(const char * fileName)
{
    struct stat st;

    jsonFileName = fileName;

    if (stat(fileName, &st)==-1) {
	printf("Cant find %s file\n", fileName);
	return false;
    }

    int fd = open(fileName, O_RDONLY);
    if (fd==-1){
	printf("Cant open %s file\n", fileName);
	return false;
    }

    rawJSON = (char *) malloc (st.st_size+1); 

    if (st.st_size!=read(fd, rawJSON, st.st_size))
    {
	printf("Cant read %s file\n", fileName);
	close(fd);
	return false;
    }
    close(fd);
    rawJSON[st.st_size]='\0';

    json = nx_json_parse(rawJSON, 0);
    if (json){
	initFromJSON();
	return true;
    }
    
    return false;
}

bool TModel::createProject(){
	
	std::string project_path = data.path + "projects/";
	
	mkdir(std::string(project_path + data.name).c_str(), 0x1FF);
	mkdir(std::string(project_path + data.name + "/src").c_str(), 0x1FF);
	mkdir(std::string(project_path + data.name + "/src/model").c_str(), 0x1FF);
	mkdir(std::string(project_path + data.name + "/build").c_str(), 0x1FF);
	mkdir(std::string(project_path + data.name + "/iterations").c_str(), 0x1FF);

	int ret = true;
	for(int i = 0; i < FILES_COUNT; i ++)
	    if (!createFile(std::string("prj_templates/") + files_list[i], project_path + data.name + files_list[i])){
		printf("Cant create file %s \n", std::string(project_path + data.name + files_list[i]).c_str());
		ret = false;
		}

	return ret;
}


bool TModel::createIteration0(){

    std::ofstream out_file(/*data.path + "projects/" + data.name +*/ data.iterPath + "/0.xml");

    if (!out_file.is_open()) return false;

    out_file << "<states>" << std::endl;
    out_file << "<itno>0</itno>" << std::endl;
    out_file << "<environment>" << std::endl;

    out_file << createIterationConstants();

    out_file << "</environment>" << std::endl;


    for(int id = 0; id < data.vertices.size(); id++){
	out_file << std::endl << "<xagent>" << std::endl;
	out_file << "<name>vertice</name>" << std::endl;
	out_file << "<id>" << std::to_string(id) << "</id>" << std::endl;;
	out_file << "<value>" << std::to_string(data.vertices[id].value) << "</value>" << std::endl;
	out_file << "<previous>";

	float imp_value = 0;
	for(std::vector<TImpulse>::iterator imp_iter = data.impulses.begin(); imp_iter != data.impulses.end(); imp_iter++){
		if (imp_iter->step == 0 && imp_iter->v == data.vertices[id].id){
			imp_value = imp_iter->value * (-1);
			break;
		}
	}
	out_file << std::to_string(imp_value);
	out_file << "</previous>" << std::endl;

	if (id < data.lags.size()){
	    out_file << "<max_lag>" << std::to_string(data.lags[id]) << "</max_lag>" << std::endl;
	}

	out_file << "<edges>";
	for (int to_id = 0; to_id < data.vertices.size(); to_id++){
	    out_file << std::to_string(get_weight(to_id, id));//id, to_id));
	    if (to_id < data.vertices.size() - 1) out_file << ",";
	}
	out_file << "</edges>" << std::endl;

	out_file << "</xagent>" << std::endl;
    }

    out_file << std::endl << "</states>" << std::endl;
    return true;


    return true;
}

bool TModel::makeProject(){

    chmod(std::string(data.path + "projects/" + data.name + "/make.sh").c_str(), S_IRWXU|S_IRWXG|S_IRWXO);
    int res = std::system(std::string(data.path + "projects/" + data.name + "/make.sh").c_str());
    if (res != 0)
	printf("!!! Model make : ERROR (%d) \n", res);
    else{
	printf("!!! Model make : OK\n");
    }
    return true;
}

bool TModel::runProject(){
    chmod(std::string(data.path + "projects/" + data.name + "/run.sh").c_str(), S_IRWXU|S_IRWXG|S_IRWXO);
    int res = std::system(std::string(data.path + "projects/" + data.name + "/run.sh").c_str());
    if (res != 0)
		printf("!!! Model run : ERROR (%d) \n", res);
    else
		printf("!!! Model run : OK\n");
    return true;
}

bool TModel::createFile(std::string from, std::string to){

    std::ifstream in_file(from);
    std::ofstream out_file(to);
    std::string line;

    if (!in_file.is_open() || !out_file.is_open()) return false;

    while(getline(in_file, line))
	out_file << convert_string(line) << std::endl;

    in_file.close();
    out_file.close();

    return true;
}

bool TModel::copyFile(std::string from, std::string to){

    std::ifstream in_file(from);
    std::ofstream out_file(to);
    std::string line;

    if (!in_file.is_open() || !out_file.is_open()) return false;

    while(getline(in_file, line))
	out_file << line << std::endl;

    in_file.close();
    out_file.close();

    return true;
}

std::string TModel::getXMLConstant()
{
    std::string out;

    out +=  "	<gpu:variable>\n";
    out +=  "	<type>int</type>\n";
    out +=  "	<name>VERTICES_COUNT</name>\n";
    out +=  "	<defaultValue>"+ std::to_string(data.vertices.size()) +"</defaultValue>\n";
    out +=  "	</gpu:variable>\n";

    return out;
}

std::string TModel::createIterationConstants()
{
    std::string out;
    out =  "\n";
    return out;
}

std::string TModel::getXMLAgentVar()
{
    std::string out;

    out += "	<gpu:variable>\n";
    out += "		<type>int</type>\n";
    out += "		<name>id</name>\n";
    out += "	</gpu:variable>\n";

    out += "	<gpu:variable>\n";
    out += "		<type>float</type>\n";
    out += "		<name>value</name>\n";
    out += "	</gpu:variable>\n";

    out += "	<gpu:variable>\n";
    out += "		<type>float</type>\n";
    out += "		<name>add_value</name>\n";
    out += "		<defaultValue>0</defaultValue>\n";
    out += "	</gpu:variable>\n";

    out += "	<gpu:variable>\n";
    out += "		<type>float</type>\n";
    out += "		<name>previous</name>\n";
    out += "	</gpu:variable>\n";

    out += "	<gpu:variable>\n";
    out += "		<type>int</type>\n";
    out += "		<name>max_lag</name>\n";
    out += "	</gpu:variable>\n";

    out += "	<gpu:variable>\n";
    out += "		<type>int</type>\n";
    out += "		<name>current_lag</name>\n";
    out += "		<defaultValue>0</defaultValue>\n";
    out += "	</gpu:variable>\n";

    out += "	<gpu:variable>\n";
    out += "		<type>int</type>\n";
    out += "		<name>edges</name>\n";
    out += "		<arrayLength>"+std::to_string(data.vertices.size())+"</arrayLength>\n";
    out += "	</gpu:variable>\n";

    return out;
}

std::string TModel::convert_string(std::string in)
{
    std::string out = in;
    std::size_t pos;

    // %%NAME%%
    while((pos = out.find("%%NAME%%")) != std::string::npos)
		out.replace(pos, std::string("%%NAME%%").length(), data.name);

    // %%PATH%%
    while((pos = out.find("%%PATH%%")) != std::string::npos)
		out.replace(pos, std::string("%%PATH%%").length(), data.path);

    // %%ITER_PATH%%
    while((pos = out.find("%%ITER_PATH%%")) != std::string::npos)
		out.replace(pos, std::string("%%ITER_PATH%%").length(), (data.iterPath));

    // %%ITER_PATH%%
    while((pos = out.find("%%ITER%%")) != std::string::npos)
		out.replace(pos, std::string("%%ITER%%").length(), std::to_string(data.iterCount) );

    // %%VISUAL%%
    while((pos = out.find("%%VISUAL%%")) != std::string::npos)
		out.replace(pos, std::string("%%VISUAL%%").length(), std::to_string(data.visual));

    // %%XML_CONSTANT%%
    while((pos = out.find("%%XML_CONSTANT%%")) != std::string::npos)
		out.replace(pos, std::string("%%XML_CONSTANT%%").length(), getXMLConstant());

    // %%XML_AGENT_VAR%%
    while((pos = out.find("%%XML_AGENT_VAR%%")) != std::string::npos)
		out.replace(pos, std::string("%%XML_AGENT_VAR%%").length(), getXMLAgentVar());

    return out;
}



