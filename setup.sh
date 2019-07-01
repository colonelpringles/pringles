#!/bin/bash

BASE_PRINGLES_DIR=$(pwd)
CDPP_BIN_DIR=$BASE_PRINGLES_DIR/cdpp/src/bin

# Clone git submodules recursively (eg. CD++ Simulator)
git submodule update --init --recursive

# Build simulator to generate binaries
make -C cdpp/src/

# Generate pringles.config file
echo "CDPP_BIN_PATH = '$CDPP_BIN_DIR'" >  colonel/wrapper/config.py