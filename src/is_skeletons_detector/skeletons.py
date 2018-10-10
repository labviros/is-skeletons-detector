import cv2
import numpy as np
import tensorflow as tf

from .utils import get_np_image, get_links
from .options_pb2 import SkeletonsDetectorOptions
from is_msgs.image_pb2 import Image, ObjectAnnotations, ObjectLabels, HumanKeypoints

from tf_pose import common
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh


class SkeletonsDetector:
    def __init__(self, options):
        if not isinstance(options, SkeletonsDetectorOptions):
            raise Exception(
                'Invalid parameter on \'SkeletonsDetector\' constructor: not a SkeletonsDetectorOptions type'
            )
        self._op = options

        model = '{}x{}'.format(self._op.resize.width, self._op.resize.height)
        w, h = model_wh(model)
        self._resize_to_default = (w > 0 and h > 0)
        model_name = SkeletonsDetectorOptions.Model.Name(self._op.model).lower()

        graph_path = get_graph_path(model_name=model_name)
        gpu_options = tf.GPUOptions(
            allow_growth=self._op.gpu_mem_allow_growth,
            per_process_gpu_memory_fraction=self._op.per_process_gpu_memory_fraction)
        tf_config = tf.ConfigProto(gpu_options=gpu_options)

        self._estimator = TfPoseEstimator(
            graph_path=graph_path, target_size=(w, h), tf_config=tf_config)

        self._to_sks_part = {
            0: HumanKeypoints.Value('NOSE'),
            1: HumanKeypoints.Value('NECK'),
            2: HumanKeypoints.Value('RIGHT_SHOULDER'),
            3: HumanKeypoints.Value('RIGHT_ELBOW'),
            4: HumanKeypoints.Value('RIGHT_WRIST'),
            5: HumanKeypoints.Value('LEFT_SHOULDER'),
            6: HumanKeypoints.Value('LEFT_ELBOW'),
            7: HumanKeypoints.Value('LEFT_WRIST'),
            8: HumanKeypoints.Value('RIGHT_HIP'),
            9: HumanKeypoints.Value('RIGHT_KNEE'),
            10: HumanKeypoints.Value('RIGHT_ANKLE'),
            11: HumanKeypoints.Value('LEFT_HIP'),
            12: HumanKeypoints.Value('LEFT_KNEE'),
            13: HumanKeypoints.Value('LEFT_ANKLE'),
            14: HumanKeypoints.Value('RIGHT_EYE'),
            15: HumanKeypoints.Value('LEFT_EYE'),
            16: HumanKeypoints.Value('RIGHT_EAR'),
            17: HumanKeypoints.Value('LEFT_EAR'),
        }

    '''
        @detect, image argument can be either a np.darray matrix
                 or an is_msgs.image_pb2.Image
    '''

    def detect(self, image):
        _image = get_np_image(image)
        humans = self._estimator.inference(
            npimg=_image,
            resize_to_default=self._resize_to_default,
            upsample_size=self._op.resize_out_ratio)

        im_h, im_w = _image.shape[:2]
        return self._to_object_annotations(humans, im_w, im_h)

    def _to_object_annotations(self, humans, im_width, im_height):
        obs = ObjectAnnotations()
        for human in humans:
            ob = obs.objects.add()
            for part_id, bp in human.body_parts.items():
                part = ob.keypoints.add()
                part.id = self._to_sks_part[part_id]
                part.position.x = bp.x * im_width
                part.position.y = bp.y * im_height
                part.score = bp.score
            ob.label = "human_skeleton"
            ob.id = ObjectLabels.Value('HUMAN_SKELETON')
        obs.resolution.width = im_width
        obs.resolution.height = im_height
        return obs