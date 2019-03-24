Skeletons Detection Service
===

Streams
---

| Name | Input (Topic/Message) | Output (Topic/Message) | Description |
| ---- | --------------------- | ---------------------- | ----------- |
| SkeletonsDetector.Detection | **CameraGateway.\d+.Frame** [Image] | **SkeletonsDetector.\d+.Detection** [ObjectAnnotations] | Detect skeletons on images published by cameras and publishes an ObjectAnnotations message containing all the skeletons detected |
| SkeletonsDetector.Detection | **CameraGateway.\d+.Frame** [Image] | **SkeletonsDetector.\d+.Rendered** [Image] | After detection, skeletons are drew on input image and published for visualization. **NOTE:** *This stream will be deprecated after [mjpeg server](https://github.com/labviros/is-mjpeg-server) became able to render any [ObjectAnnotations]* |



RPCs
---
| Service | Request | Reply | Description |
| ------- | ------- | ------| ----------- |
| SkeletonsDetector.Detect | [Image] | [ObjectAnnotations] | Same purpose of stream shown above, but offered with a RPC server. |

[Image]: https://github.com/labviros/is-msgs/blob/modern-cmake/docs/README.md#is.vision.Image
[ObjectAnnotations]: https://github.com/labviros/is-msgs/blob/modern-cmake/docs/README.md#is.vision.ObjectAnnotations


About
---

This detector uses [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) method. You can choose between three available models, `COCO`, with 15 joints,  and `MPI` or `MPI_4_layers`, with 18 joints. These joints are identified by a subset of an enumeration message called [HumanKeypoints](https://github.com/labviros/is-msgs/blob/modern-cmake/docs/README.md#humankeypoints). Moreover, you can choose others parameters that influence on speed and accuracy. See the [options.proto](https://github.com/labviros/is-skeletons-detector/blob/openpose/src/is/conf/options.proto) file for more information.

the CNN (Convolutional Neural Network) input size changing `width` and `height` parameters of `resize` field on `options.json` file. Both must be multiples of 16. The CNN output layer can also be resize, for that change the parameter `resize_out_ratio`. Both parameters impact on detection time and quality.

 
Developing
---

Since it's necessary to install many dependencies including NVIDIA Cuda libraries, a Docker image can be created to ease the development process. To do so, run the command below on the root directory of this project:

```shell
docker build . --network=host -f etc/docker/Dockerfile.devel -t is-skeletons-detector/devel
```

Besides, you'll need to download the available network models. Do that running the following commands:

```shell
cd etc/dataset
./download.sh
```

Now, you can compile and run the binaries from inside the generated docker image by running on the root directory:

```shell
docker run -ti --runtime=nvidia --network=host -v `pwd`:/project -v `pwd`/etc/dataset/models:/models is-skeletons-detector/devel /bin/bash
```

Images for production are built automatically by [Docker Cloud](https://cloud.docker.com/) after a commit being tagged on GitHub. Otherwise, you can do this on your machine by building the another Dockerfile on `etc/docker/` folder like you did for the developer image.