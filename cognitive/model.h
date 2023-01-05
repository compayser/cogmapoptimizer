#ifndef __MODEL_H__
#define __MODEL_H__

#include "nxjson.h"
#include <string>
#include <vector>

struct TVertice{
    std::string		name;
    std::string		token;
    unsigned long	id;
    float		value;
    float		growth;

    float	min;
    float	max;
    int		need_test;
    int		correct;
};

struct TEdge{
    std::string		name;
    std::string		formula;

    float		weight;

    unsigned long	id;
    unsigned long	v1;
    unsigned long	v2;

    int		v1_id;
    int		v2_id;
};

struct TImpulse{
    float		value;
    unsigned long	v;
    int			step;
};

struct modelData{
    std::string	name;
    int		visual;
    std::string	path;
    std::string	iterPath;
    int		iterCount;

    std::vector<TVertice>	vertices;
    std::vector<TEdge>		edges;
    std::vector<TImpulse>	impulses;
    std::vector<int>		lags;
};

struct iterXMLData{
    int num;
    std::vector<TVertice> vert;
};

class TModel {
    private: 
	struct modelData	data;
	std::vector<iterXMLData>	xml_analize;

	bool set_vert(std::vector<TEdge> &e,std::vector<TVertice> v);
	float  get_weight(int id, int to_id);


	static TModel * p_instance;
	TModel();
	~TModel();
	TModel(const TModel&);
	TModel& operator= (TModel&);

    // Работа с JSON форматом входных данных
	std::string jsonFileName;
	char * rawJSON;
	const nx_json * json;

	char * compile_rawJSON;
	const nx_json * compile_json;

	std::string jsonFileName_group;
	char * rawJSON_group;
	const nx_json * json_group;

	char * compile_rawJSON_group;
	const nx_json * compile_json_group;


	void initFromJSON();
	void initFromJSON_group();

    // Входные данные
	std::string getXMLConstant();
	std::string getXMLAgentVar();
	std::string createIterationConstants();

	bool createFile(std::string from, std::string to);
	bool copyFile(std::string from, std::string to);
	std::string convert_string(std::string in);

    public:
	static TModel* getInstance() {
		if (!p_instance)
			p_instance = new TModel();
		return p_instance;
	}

	bool loadFromJSON(const char * fileName, const char * fileName_group);

	bool createProject();
	bool createIteration0();
	bool makeProject();
	bool runProject();

	bool analiseXMLResult();
};

#endif

