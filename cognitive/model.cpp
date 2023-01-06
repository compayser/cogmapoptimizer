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

#include "dirent.h"

#include <algorithm>

#define FILES_COUNT 5


bool compare_iter_by_num(const iterXMLData &a, const iterXMLData &b){
    return a.num < b.num;
}

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

//    printf("data.name=[%s]\n", data.name.c_str());

    if ( (read = getline(&line, &len, fp) ) != -1)
	data.visual = atoi(line);

    if ( (read = getline(&line, &len, fp) ) != -1){
	line[strlen(line) - 1] = '\0';
	data.path = line;
    }

//    printf("data.path=[%s]\n", data.path.c_str());

    if ( (read = getline(&line, &len, fp) ) != -1){
	line[strlen(line) - 1] = '\0';
	data.iterPath = line + data.name + "/iterations/";
    }

//    printf("data.iterPath=[%s]\n", data.iterPath.c_str());

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


float  TModel::get_weight(int id, int to_id){

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
	if (retData_2->text_value != NULL) {
	    //printf("Vertice name: [%s]\n", retData_2->text_value);
	    tmp_vert.name = retData_2->text_value;
	}
	else{
	    printf("Vertice name NOT SET!\n");
        }

	//"id":1655712545685
	retData_2 = nx_json_get(retArrayData, "id");
	//printf("Vertice ID: [%ld]\n", retData_2->int_value);
	tmp_vert.id = retData_2->int_value;

	retData_2 = nx_json_get(retArrayData, "value");
	//printf("Vertice value: [%f]\n", (float)retData_2->dbl_value);
	tmp_vert.value = (float)retData_2->dbl_value;

	retData_2 = nx_json_get(retArrayData, "growth");
	//printf("Vertice growth: [%f]\n", (float)retData_2->dbl_value);
	tmp_vert.growth = (float)retData_2->dbl_value;

	tmp_vert.need_test = 0;
	tmp_vert.min = 0;
	tmp_vert.max = 0;

	data.vertices.push_back(tmp_vert);
	//printf("\n");

	retArrayData = retArrayData->next;
    }

    retData = nx_json_get(json, "Edges");
    retArrayData = retData->child;
    while (retArrayData != NULL) {
// {"color":"0x808080ff","md":"(207.0,65.0)","weight":1.0,"formula":"","id":1655712630647,"v1":1655712545685,"shortName":"","v2":1655712594662},
	TEdge	tmp_edge;

	retData_2 = nx_json_get(retArrayData, "shortName");
	if (retData_2->text_value != NULL) {
		//printf("Edge shortName: [%s]\n", retData_2->text_value);
		tmp_edge.name = retData_2->text_value;
	}
	else
	{
	    printf("Edge shortname NOT SET\n");
	}

	retData_2 = nx_json_get(retArrayData, "formula");
	if (retData_2->text_value != NULL) {
		//printf("Edge formula: [%s]\n", retData_2->text_value);
		tmp_edge.formula = retData_2->text_value;
	}
	else
	{
	    //printf("Edge formula NOT SET\n");
	}

	retData_2 = nx_json_get(retArrayData, "id");
	//printf("Edge ID: [%ld]\n", retData_2->int_value);
	tmp_edge.id = retData_2->int_value;

	retData_2 = nx_json_get(retArrayData, "v1");
	//printf("Edge ID V1: [%ld]\n", retData_2->int_value);
	tmp_edge.v1 = retData_2->int_value;

	retData_2 = nx_json_get(retArrayData, "v2");
	//printf("Edge ID V2: [%ld]\n", retData_2->int_value);
	tmp_edge.v2 = retData_2->int_value;

	retData_2 = nx_json_get(retArrayData, "weight");
	//printf("Edge weight: [%f]\n", retData_2->dbl_value);
	tmp_edge.weight = retData_2->dbl_value;

	data.edges.push_back(tmp_edge);
	//printf("\n");

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
		//printf("Impulse ID: [%ld]\n", retData_2->int_value);
		tmp_impulse.v = retData_2->int_value;

		retData_2 = nx_json_get(retArrayData, "step");
		//printf("Impulse step: [%ld]\n", retData_2->int_value);
		tmp_impulse.step = retData_2->int_value;
    
		retData_2 = nx_json_get(retArrayData, "val");
		//printf("Impulse val: [%f]\n", retData_2->dbl_value);
		tmp_impulse.value = retData_2->dbl_value;

		data.impulses.push_back(tmp_impulse);
		//printf("\n");

		retArrayData = retArrayData->next;
	}// while (retArrayData != NULL) {

	beforeDataArray = beforeDataArray->next;
    }// while(beforeDataArray != NULL) {


    set_vert(data.edges, data.vertices);
}


void TModel::initFromJSON_group()
{
    const nx_json * retData;
    const nx_json * retArrayData;
    const nx_json * retData_2;

    retData = nx_json_get(json_group, "Groups");
    retArrayData = retData->child;
    while (retArrayData != NULL) {
// {"color":"0x808080ff","show":"false","x":144.0,"fullName":"К1","y":64.0,"growth":0.0,"id":1655712545685,"shortName":"V1","value":0.0},

	unsigned long id = 0;
	float min = 0;
	float max = 0;
	int need_test = 0;

	retData_2 = nx_json_get(retArrayData, "id");
	//printf("Groups ID: [%ld]\n", retData_2->int_value);
	id = retData_2->int_value;

	retData_2 = nx_json_get(retArrayData, "min");
	//printf("Groups min: [%f]\n", retData_2->dbl_value);
	min = retData_2->dbl_value;

	retData_2 = nx_json_get(retArrayData, "max");
	//printf("Groups min: [%f]\n", retData_2->dbl_value);
	max = retData_2->dbl_value;

	retData_2 = nx_json_get(retArrayData, "type");
	if (strcmp(retData_2->text_value, "Y") == 0) need_test = 1;
	else need_test = 0;

	if (need_test){
	    for(int i = 0; i < data.vertices.size(); i++){
		if (id == data.vertices[i].id){
			data.vertices[i].min = min;
			data.vertices[i].max = max;
			data.vertices[i].need_test = need_test;
	        }
	    }
	}

	//printf("\n");
	retArrayData = retArrayData->next;
    }
}

bool TModel::loadFromJSON(const char * fileName, const char * fileName_group)
{
    struct stat st;
    struct stat st_group;


    jsonFileName = fileName;
    jsonFileName_group = fileName_group;

    if (stat(fileName, &st)==-1) {
	printf("Cant find %s file\n", fileName);
	return false;
    }

    if (stat(fileName_group, &st_group)==-1) {
	printf("Cant find %s file\n", fileName_group);
	return false;
    }

    int fd = open(fileName, O_RDONLY);
    if (fd==-1){
	printf("Cant open %s file\n", fileName);
	return false;
    }

    int fd_group = open(fileName_group, O_RDONLY);
    if (fd_group==-1){
	printf("Cant open %s file\n", fileName_group);
	return false;
    }


    rawJSON = (char *) malloc (st.st_size+1); 
    rawJSON_group = (char *) malloc (st_group.st_size+1); 

    if (st.st_size!=read(fd, rawJSON, st.st_size))
    {
	printf("Cant read %s file\n", fileName);
	close(fd);
	return false;
    }
    close(fd);
    rawJSON[st.st_size]='\0';

    if (st_group.st_size!=read(fd_group, rawJSON_group, st_group.st_size))
    {
	printf("Cant read %s file\n", fileName_group);
	close(fd_group);
	return false;
    }
    close(fd_group);
    rawJSON_group[st_group.st_size]='\0';


    json = nx_json_parse(rawJSON, 0);
    if (json){
	initFromJSON();

	json_group = nx_json_parse(rawJSON_group, 0);
	if (json_group)
	    initFromJSON_group();

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

bool TModel::analiseXMLResult()
{

    DIR *dir;
    size_t len  = 0;
    char * str_line = NULL;

    if ( (dir = opendir(data.iterPath.c_str())) == NULL){
	printf("Cant open dir %s\n", data.iterPath.c_str());
    }
    else{
	printf("Work with data - %s\n", data.iterPath.c_str());
	struct dirent * f_cur;
	while ((f_cur = readdir(dir)) != NULL){
	    FILE * fp = fopen(std::string(data.iterPath + f_cur->d_name).c_str(), "r");
	    if (fp != NULL){
		printf("%s\n", f_cur->d_name);
		iterXMLData cur_iter;
		std::size_t pos;
		bool is_iteration_xml = false;
		while ( (getline(&str_line, &len, fp) ) != -1) {
		    std::string line(str_line);
		    if ((pos = line.find("<itno>")) != std::string::npos){
			int iter = 0;
			std::sscanf(line.c_str(), "<itno>%d</itno>", &iter);
			cur_iter.num = iter;
			//printf("N iter = %d [%s]\n", cur_iter.num, line.c_str());
			is_iteration_xml = true;
			break;
		    }
		}

		if (is_iteration_xml){
			TVertice vert_temp;

			while ( (getline(&str_line, &len, fp) ) != -1) {
			    std::string line(str_line);
			    char temp_token[256];
			    memset(temp_token, 0, sizeof(char)*256);
			    if ((pos = line.find("</states>")) != std::string::npos) break;
			
			    if ((pos = line.find("<id>")) != std::string::npos) std::sscanf(line.c_str(), "<id>%d</id>", &vert_temp.id);
			    if ((pos = line.find("<value>")) != std::string::npos) std::sscanf(line.c_str(), "<value>%f</value>", &vert_temp.value);
			    if ((pos = line.find("<token>")) != std::string::npos)
			    {
				std::sscanf(line.c_str(), "<token>%s</token>", &temp_token[0]);
				vert_temp.token = std::string(temp_token).substr(0, std::string(temp_token).find("</token>"));
				//printf("[%s]\n", vert_temp.token.c_str());
			    }
			    if ((pos = line.find("<min>")) != std::string::npos) std::sscanf(line.c_str(), "<min>%f</min>", &vert_temp.min);
			    if ((pos = line.find("<max>")) != std::string::npos) std::sscanf(line.c_str(), "<max>%f</max>", &vert_temp.max);
			    if ((pos = line.find("<correct>")) != std::string::npos) std::sscanf(line.c_str(), "<correct>%d</correct>", &vert_temp.correct);
			    if ((pos = line.find("<need_test>")) != std::string::npos) std::sscanf(line.c_str(), "<need_test>%d</need_test>", &vert_temp.need_test);
	
			    if ((pos = line.find("</xagent>")) != std::string::npos) {
				cur_iter.vert.push_back(vert_temp);
				//printf("vert ->%d %f %f %f %d %d\n", vert_temp.id, vert_temp.value, vert_temp.min, vert_temp.max, vert_temp.need_test, vert_temp.correct);
			    }

			}
			xml_analize.push_back(cur_iter);
		}// if (is_iteration_xml)
	    }
	    //else printf("Skip %s\n", std::string(data.iterPath + f_cur->d_name).c_str());
	}
	closedir(dir);
    }

    if (xml_analize.empty()) return false;

    std::sort(xml_analize.begin(), xml_analize.end(), compare_iter_by_num);

    std::vector<int> need_test_vert;

    FILE * f_rezult = fopen(std::string(data.iterPath + "result.txt").c_str(), "w+");
    fprintf(f_rezult, "Отслеживаемые вершины:\n");
    for (int i = 0; i < xml_analize[0].vert.size(); i++) {
	if (xml_analize[0].vert[i].need_test){
	    fprintf(f_rezult, "Вершина:");
	    fprintf(f_rezult, " %s", xml_analize[0].vert[i].token.c_str());
	    fprintf(f_rezult, ", Проверяемый диапазон: [%f-%f]\n", xml_analize[0].vert[i].min, xml_analize[0].vert[i].max);
	    fprintf(f_rezult, "	Итерации на которых значение не попадает в допустимый диапазон:\n		");
	    for(int j = 1; j < xml_analize.size(); j++){
		for(int k = 1; k < xml_analize[j].vert.size(); k++){
			if (xml_analize[0].vert[i].id == xml_analize[j].vert[k].id && (!xml_analize[j].vert[k].correct))
			    fprintf(f_rezult,"%d ", j);
		}
	    }

	    fprintf(f_rezult, "\n	Итерации на которых значение попадает в допустимый диапазон:\n		");
	    for(int j = 1; j < xml_analize.size(); j++){
		for(int k = 1; k < xml_analize[j].vert.size(); k++){
			if (xml_analize[0].vert[i].id == xml_analize[j].vert[k].id && xml_analize[j].vert[k].correct)
			    fprintf(f_rezult,"%d ", j);
		}
	    }
	    fprintf(f_rezult, "\n");

	}
    }
    fprintf(f_rezult, "");

    fclose(f_rezult);

    return true;
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
	out_file << "<token>" << std::to_string(data.vertices[id].id) << "</token>" << std::endl;;
	out_file << "<previous>0";
	out_file << "</previous>" << std::endl;

	//out_file << "<impulse>";
	float imp_value = 0;
	for(std::vector<TImpulse>::iterator imp_iter = data.impulses.begin(); imp_iter != data.impulses.end(); imp_iter++){
		if (imp_iter->step == 1 && imp_iter->v == data.vertices[id].id){
			imp_value = imp_iter->value ;// * (-1);
			break;
		}
	}
	//out_file << std::to_string(imp_value + /*(-1)**/data.vertices[id].growth);
	//out_file << "</impulse>" << std::endl;

	out_file << "<value>" << std::to_string(imp_value + data.vertices[id].growth + data.vertices[id].value) << "</value>" << std::endl;

	if (id < data.lags.size()){
	    out_file << "<max_lag>" << std::to_string(data.lags[id]) << "</max_lag>" << std::endl;
	}

	out_file << "<edges>";
	for (int to_id = 0; to_id < data.vertices.size(); to_id++){
	    out_file << std::to_string(get_weight(to_id, id));//id, to_id));
	    if (to_id < data.vertices.size() - 1) out_file << ",";
	}
	out_file << "</edges>" << std::endl;

	out_file << "<min>" << std::to_string(data.vertices[id].min) << "</min>" << std::endl;;
	out_file << "<max>" << std::to_string(data.vertices[id].max) << "</max>" << std::endl;;
	out_file << "<need_test>" << std::to_string(data.vertices[id].need_test) << "</need_test>" << std::endl;;

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
    out += "		<type>float</type>\n";
    out += "		<name>edges</name>\n";
    out += "		<arrayLength>"+std::to_string(data.vertices.size())+"</arrayLength>\n";
    out += "	</gpu:variable>\n";

    out += "	<gpu:variable>\n";
    out += "		<type>float</type>\n";
    out += "		<name>min</name>\n";
    out += "	</gpu:variable>\n";

    out += "	<gpu:variable>\n";
    out += "		<type>float</type>\n";
    out += "		<name>max</name>\n";
    out += "	</gpu:variable>\n";

    out += "	<gpu:variable>\n";
    out += "		<type>int</type>\n";
    out += "		<name>need_test</name>\n";
    out += "	</gpu:variable>\n";

    out += "	<gpu:variable>\n";
    out += "		<type>int</type>\n";
    out += "		<name>correct</name>\n";
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


//===============================================================================================
//
//   UNIT TESTS
//===============================================================================================

#include "minunit.h"

int tests_run = 0;

int value = 0;

static char * test_init_model(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error,TModel::getInstance() == NULL", "passed, TModel::getInstance()!=NULL",  test_m != NULL);
    return 0;
}

static char * test_init_json_vert_count(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error, unit-test.cmj vertices count, test_m->data.vertices.size() != 17", "passed, unit-test.cmj vertices count == 17", test_m->data.vertices.size() == 17);
    return 0;
}

static char * test_init_json_edge_count(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error, unit-test.cmj edges count, test_m->data.edges.size() != 57", "passed, unit-test.cmj edges count == 57", test_m->data.edges.size() == 57);
    return 0;
}

static char * test_init_json_test_0_vert_id(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error, unit-test.cmj vertices[0] id != 1655712545685ULL", "passed, unit-test.cmj vertices[0] id == 1655712545685ULL", test_m->data.vertices[0].id == 1655712545685ULL);
    return 0;
}

static char * test_init_json_test_0_vert_name(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error, unit-test.cmj vertices[0] name != K1", "passed, unit-test.cmj vertices[0] name == K1", test_m->data.vertices[0].name.compare("K1") );
    return 0;
}

static char * test_init_json_test_0_vert_value(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error, unit-test.cmj vertices[0] (value - 1.90) < 0.0000001", "passed, unit-test.cmj vertices[0] (value - 1.90) < 0.0000001", (test_m->data.vertices[0].value - 1.90) < 0.0000001 );
    return 0;
}

static char * test_init_json_test_0_vert_growth(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error, unit-test.cmj vertices[0] (growth - 0.1) < 0.0000001", "passed, unit-test.cmj vertices[0] (growth - 0.1) < 0.0000001", (test_m->data.vertices[0].growth - 0.1) < 0.0000001 );
    return 0;
}

static char * test_init_json_test_0_edge_id(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error, unit-test.cmj edges[0] id != 1655712630647ULL", "passed, unit-test.cmj edges[0] id == 1655712630647ULL", test_m->data.edges[0].id == 1655712630647ULL);
    return 0;
}

static char * test_init_json_test_0_edge_v1(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error, unit-test.cmj edges[0] v1 != 1655712545685ULL", "passed, unit-test.cmj edges[0] v1 == 1655712545685ULL", test_m->data.edges[0].v1 == 1655712545685ULL);
    return 0;
}

static char * test_init_json_test_0_edge_v2(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error, unit-test.cmj edges[0] v2 != 1655712594662ULL", "passed, unit-test.cmj edges[0] v2 == 1655712594662ULL", test_m->data.edges[0].v2 == 1655712594662ULL);
    return 0;
}

static char * test_init_json_test_0_edge_weight(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error, unit-test.cmj edges[0] (weight - 0.1) < 0.0000001", "passed, unit-test.cmj edges[0] (weight - 0.1) < 0.0000001", (test_m->data.edges[0].weight - 0.1) < 0.0000001 );
    return 0;
}

static char * test_init_json_test_0_group(){
    TModel * test_m = TModel::getInstance();
    mu_assert("error, unit-test-group.cmj_xyz id", "passed, unit-test-group.cmj_z edges[0] (weight - 0.1) < 0.0000001", (test_m->data.edges[0].weight - 0.1) < 0.0000001 );
    return 0;
}


static char * all_tests() {
    mu_run_test(test_init_model);

    mu_run_test(test_init_json_vert_count);
    mu_run_test(test_init_json_edge_count);

    mu_run_test(test_init_json_test_0_vert_id);
    mu_run_test(test_init_json_test_0_vert_name);
    mu_run_test(test_init_json_test_0_vert_value);
    mu_run_test(test_init_json_test_0_vert_growth);

    mu_run_test(test_init_json_test_0_edge_id);
    mu_run_test(test_init_json_test_0_edge_v1);
    mu_run_test(test_init_json_test_0_edge_v2);
    mu_run_test(test_init_json_test_0_edge_weight);

    return 0;
}

void unit_tests(){
    
    printf("TESTS:\n");

    char * result = all_tests();
    if (result != 0) {
	printf("%s\n", result);
    }
    else {
	printf("ALL TESTS PASSED\n");
    }
    
    printf("Tests run: %d\n", tests_run);
}

