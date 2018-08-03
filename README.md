Skeletons Detection Service
===

Streams
---

| Name | Input (Topic/Message) | Output (Topic/Message) | Description |
| ---- | --------------------- | ---------------------- | ----------- |
| Skeletons.Detection | **CameraGateway.\d+.Frame** [Image] | **Skeletons.\d+.Detection** [ObjectAnnotations] | Detect skeletons on images published by cameras and publishes an ObjectAnnotations message containing all the skeletons detected |
| Skeletons.Detection | **CameraGateway.\d+.Frame** [Image] | **Skeletons.\d+.Rendered** [Image] | After detection, skeletons are drew on input image and published for visualization. **NOTE:** *This stream will be deprecated after [mjpeg server](https://github.com/labviros/is-mjpeg-server) became able to render any [ObjectAnnotations]* |

[Image]: https://github.com/labviros/is-msgs/blob/modern-cmake/docs/README.md#is.vision.Image
[ObjectAnnotations]: https://github.com/labviros/is-msgs/blob/modern-cmake/docs/README.md#is.vision.ObjectAnnotations


About
---

This detector uses an [implementation](https://github.com/ildoonet/tf-pose-estimation) based on [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose) method. You can choose between two available models, `CMU` or `MOBILENET_THIN`, both are based on COCO Model that contains 18 joints. These joints are identified by a subset of an enumeration message called [HumanKeypoints](https://github.com/labviros/is-msgs/blob/modern-cmake/docs/README.md#humankeypoints). The joints of COCO model are: *NOSE*, *NECK*, *RIGHT_SHOULDER*, *RIGHT_ELBOW*, *RIGHT_WRIST*, *LEFT_SHOULDER*, *LEFT_ELBOW*, *LEFT_WRIST*, *RIGHT_HIP*, *RIGHT_KNEE*, *RIGHT_ANKLE*, *LEFT_HIP*, *LEFT_KNEE*, *LEFT_ANKLE*, *RIGHT_EYE*, *LEFT_EYE*, *RIGHT_EAR* and *LEFT_EAR*.

Beyond the model, you can choose the CNN (Convolutional Neural Network) input size changing `width` and `height` parameters of `resize` field on `options.json` file. Both must be multiples of 16. The CNN output layer can also be resize, for that change the parameter `resize_out_ratio`. Both parameters impact on detection time and quality.

 
Developing
---

Once it's necessary to install many dependencies including NVIDIA Cuda libraries, a Docker image is created before the deployment image. This image can be user to perform tests during development. For that, simply run the script:

```shell
bash pack.sh
```
If it is the first time you run this script, a message will be prompt indicating that the image `is-skeletons-detector/dev` wasn't found, then the build process will occur. Now just run the command below inside you directory.

```shell
docker run -ti --rm --runtime=nvidia --network=host -v `pwd`:/devel is-skeletons-detector/dev bash
```

In case you need to make any change on options protobuf file, will be necessary to rebuild the python file related to it. For do that, you can use a docker image running the command below. You can find more information about this way to build [here](https://github.com/felippe-mendonca/is-msgs-protoc-py).

```shell
docker run --rm -v `pwd`:/protos mendonca/is-msgs-protoc:1.1.7 options.proto
```