#!/bin/bash
cd $(dirname "$BASH_SOURCE")
./cognitive --project test_serg.cmj group.cmj_xyz
./cognitive --generate test_serg.cmj group.cmj_xyz
./cognitive --make test_serg.cmj group.cmj_xyz
./cognitive --run test_serg.cmj group.cmj_xyz
./cognitive --analise test_serg.cmj group.cmj_xyz
