#!/bin/bash
set -e

image_build_render='p35-alpine-opencv331'
image_count=`docker images --filter="reference=${image_build_render}" -q | wc -l`
if [[ $image_count == 0 ]]; then
    echo "Docker image ${image_build_render} not found. Building..."
    sleep 2
    docker build . -f Dockerfile.alpine_opencv -t ${image_build_render} --no-cache --network=host
fi

docker_user="viros"

function build_image {
    image_tag="${docker_user}/is-skeletons:1.2-$1"
    docker build . -f Dockerfile.$1 -t ${image_tag} --network=host --no-cache
    read -r -p "Do you want to push image ${image_tag}? [y/N] " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
        echo "Log-in as '${docker_user}' at Docker registry:"
        docker login -u ${docker_user}
        docker push ${image_tag}
    fi
}

bash get_models.sh
build_image detector