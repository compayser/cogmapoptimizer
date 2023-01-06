
#include <stdio.h>
#include <string.h>

#include "model.h"

int main(int argc, char* argv[])
{

    if (( argc >= 3 && (!strcmp(argv[1], "--help"))) || (argc != 4) ){
	printf("Syntax: \n\
	%s --help - this help\n\
	%s --project filename.json group.json - generate FLAME projects\n\
	%s --generate filename.json group.json - generate start iteration\n\
	%s --make filename.json group.json - compile project\n\
	%s --run filename.json group.json - run model\n", argv[0], argv[0], argv[0], argv[0], argv[0]);
	return 0;
    }
    else {
	TModel* model = TModel::getInstance();

	if (model->loadFromJSON(argv[2], argv[3])) {
		if (!strcmp(argv[1], "--project"))
			model->createProject();
		else
		if (!strcmp(argv[1], "--generate"))
			model->createIteration0();
		else
		if (!strcmp(argv[1], "--make"))
			model->makeProject();
		else
		if (!strcmp(argv[1], "--run"))
			model->runProject();
		else
		if (!strcmp(argv[1], "--analize"))
			model->analiseXMLResult();
		else
		if (!strcmp(argv[1], "--tests"))
			unit_tests();
		else
			printf("Wrong syntax, use --help\n");
	}
	else 
		printf("Wrong input config JSON file\n");
    }
    return 0;
}

