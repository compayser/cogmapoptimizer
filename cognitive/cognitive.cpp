
#include <stdio.h>
#include <string.h>

#include "model.h"

int main(int argc, char* argv[])
{

    if (( argc >= 2 && (!strcmp(argv[1], "--help"))) || (argc != 3) ){
	printf("Syntax: \n\
	%s --help - this help\n\
	%s --project filename.json - generate FLAME projects\n\
	%s --generate filename.json - generate start iteration\n\
	%s --make filename.json - compile project\n\
	%s --run filename.json - run model\n", argv[0], argv[0], argv[0], argv[0], argv[0]);
	return 0;
    }
    else {
	TModel* model = TModel::getInstance();

	if (model->loadFromJSON(argv[2])) {
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
			printf("Wrong syntax, use --help\n");
	}
	else 
		printf("Wrong input config JSON file\n");
    }
    return 0;
}

