#!/bin/bash
export PATH="/usr/local/cuda/bin:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda/lib64:$LD_LIBRARY_PATH"
cd $(dirname "$BASH_SOURCE")
make clean
make all debug=0
