#/bin/bash
set -e

docker run --rm -v `pwd`:/protos mendonca/is-msgs-protoc:1.1.7 options.proto
mv -vn options_pb2.py ../is_skeletons_detector