#!/bin/bash
cd $(dirname "$BASH_SOURCE")
./cognitive --project test.cmj
./cognitive --generate test.cmj
./cognitive --make test.cmj
./cognitive --run test.cmj
