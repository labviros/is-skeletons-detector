#!/bin/bash

WGET="wget --retry-connrefused --read-timeout=20 --timeout=15 -t 0 --continue -c"
BASE_DIR=`pwd`

mkdir -p models/pose
mkdir -p models/pose/coco
mkdir -p models/pose/mpi

cd models/pose/coco
$WGET http://posefs1.perception.cs.cmu.edu/OpenPose/models/pose/coco/pose_iter_440000.caffemodel
$WGET https://raw.githubusercontent.com/CMU-Perceptual-Computing-Lab/openpose/v1.4.0/models/pose/coco/pose_deploy_linevec.prototxt
cd $BASE_DIR

cd models/pose/mpi
$WGET http://posefs1.perception.cs.cmu.edu/OpenPose/models/pose/mpi/pose_iter_160000.caffemodel
$WGET https://raw.githubusercontent.com/CMU-Perceptual-Computing-Lab/openpose/v1.4.0/models/pose/mpi/pose_deploy_linevec.prototxt
$WGET https://raw.githubusercontent.com/CMU-Perceptual-Computing-Lab/openpose/v1.4.0/models/pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt
cd $BASE_DIR