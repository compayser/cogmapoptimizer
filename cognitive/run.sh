#!/bin/bash
cd $(dirname "$BASH_SOURCE")
./cognitive --project unit-test.cmj unit-test-group.cmj_xyz
./cognitive --generate unit-test.cmj unit-test-group.cmj_xyz
./cognitive --make unit-test.cmj unit-test-group.cmj_xyz
./cognitive --run unit-test.cmj unit-test-group.cmj_xyz
./cognitive --analize unit-test.cmj unit-test-group.cmj_xyz
