#!/bin/bash
cd $(dirname "$BASH_SOURCE")
./cognitive --tests unit-test.cmj unit-test-group.cmj_xyz
