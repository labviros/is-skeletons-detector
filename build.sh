#!/bin/bash

set -e 

mkdir -p build && cd build
conan install .. -s compiler.libcxx=libstdc++11 --build=missing -s is-skeletons-detector:build_type=Debug
conan build ..