FROM is-skeletons-detector/dev

ADD . /project
WORKDIR /project 
RUN bash build.sh
RUN mkdir -v -p /tmp/deploy                                             \
 && mkdir -v -p /tmp/deploy/opt/is                                      \
 && libs=`find build/ -type f -name '*.bin' -exec ldd {} \;             \
    | cut -d '(' -f 1 | cut -d '>' -f 2 | sort | uniq`                  \
 && for lib in $libs; do                                                \
        cp --verbose --parents $lib /tmp/deploy;                        \
    done                                                                \
 && cp --verbose `find build/ -type f -name '*.bin'` /tmp/deploy/opt/is \
 && cp --verbose etc/conf/options.json /tmp/deploy/opt/is               \
 && rm -rf build/

# Deployment container
FROM ubuntu:16.04
ENV LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64 \
    PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LIBRARY_PATH=/usr/local/cuda/lib64/stubs \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility
COPY --from=0 /tmp/deploy /
COPY --from=0 /models /models
WORKDIR /opt/is