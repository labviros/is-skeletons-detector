#!/bin/bash
set -e

PROJECT_DIR=`pwd`

if [ ! -f "models/graph/cmu/graph_opt.pb" ] || [ ! -f "models/graph/mobilenet_thin/graph_opt.pb" ]; then
    rm -rf models/
    if [ ! -d "tf-pose-estimation" ]; then
        git clone https://github.com/felippe-mendonca/tf-pose-estimation/
    fi

    cd tf-pose-estimation
    git reset --hard 
    cd models/graph/cmu

    sed -i '/graph_freeze.pb/d' download.sh
    sed -i '/graph.pb/d' download.sh
    bash download.sh

    cd $PROJECT_DIR
    cd tf-pose-estimation
    cp --parents models/graph/cmu/graph_opt.pb ${PROJECT_DIR}
    cp --parents models/graph/mobilenet_thin/graph_opt.pb ${PROJECT_DIR}
fi